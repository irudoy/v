from datetime import datetime, timedelta, timezone
import gzip
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import backup  # noqa: E402


NOW = datetime(2026, 7, 24, 3, 0, tzinfo=timezone.utc)


class ConfigTest(unittest.TestCase):
    def write(self, directory, body):
        path = Path(directory) / "backup.toml"
        path.write_text(body, encoding="utf-8")
        return path

    def valid(self):
        return (
            'smb_url = "smb://Junkyard/Backup"\n'
            'mount_point = "/Volumes/Backup"\n'
            'backup_subdir = "vq-memgraph"\n'
            "minimum_interval_hours = 24\n"
        )

    def test_valid_config(self):
        with tempfile.TemporaryDirectory() as directory:
            config = backup.load_config(self.write(directory, self.valid()))
        self.assertEqual(config.destination, Path("/Volumes/Backup/vq-memgraph"))
        self.assertEqual(config.container_name, "vq-memgraph-mage")

    def test_server_without_share_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            body = self.valid().replace(
                "smb://Junkyard/Backup", "smb://Junkyard"
            )
            with self.assertRaisesRegex(backup.BackupError, "specific share"):
                backup.load_config(self.write(directory, body))

    def test_interval_below_one_day_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            body = self.valid().replace(
                "minimum_interval_hours = 24",
                "minimum_interval_hours = 23",
            )
            with self.assertRaisesRegex(backup.BackupError, "less than 24"):
                backup.load_config(self.write(directory, body))

    def test_parent_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            body = self.valid().replace(
                'backup_subdir = "vq-memgraph"',
                'backup_subdir = "../vq-memgraph"',
            )
            with self.assertRaisesRegex(backup.BackupError, "safe relative"):
                backup.load_config(self.write(directory, body))


class DockerEnvironmentTest(unittest.TestCase):
    def test_desktop_context_replaces_caller_docker_settings(self):
        with mock.patch.dict(
            backup.os.environ,
            {
                "DOCKER_CONTEXT": "other-context",
                "DOCKER_HOST": "unix:///tmp/other-docker.sock",
            },
        ):
            environment = backup.docker_environment()

        self.assertEqual(environment["DOCKER_CONTEXT"], "desktop-linux")
        self.assertNotIn("DOCKER_HOST", environment)

    def test_mgconsole_receives_docker_environment(self):
        config = backup.Config(
            smb_url="smb://Junkyard/Backup",
            mount_point=Path("/Volumes/Backup"),
            backup_subdir=backup.PurePosixPath("vq-memgraph"),
            minimum_interval_hours=24,
            container_name="vq-memgraph-mage",
            mount_timeout_seconds=30,
            command_timeout_seconds=900,
        )
        with mock.patch.object(backup, "run_capture", return_value="") as capture:
            backup.docker_mgconsole(config, "RETURN 1;\n", "csv")

        self.assertEqual(
            capture.call_args.kwargs["env"]["DOCKER_CONTEXT"],
            "desktop-linux",
        )


class DueTest(unittest.TestCase):
    DESTINATION = Path("/Volumes/Backup/vq-memgraph")

    def state(self, age):
        return backup.BackupState(
            NOW - age,
            str(self.DESTINATION),
            "bundle",
        )

    def test_missing_state_is_due(self):
        due, _, _ = backup.due_status(None, self.DESTINATION, 24, NOW)
        self.assertTrue(due)

    def test_23_hours_is_not_due(self):
        due, _, next_due = backup.due_status(
            self.state(timedelta(hours=23)),
            self.DESTINATION,
            24,
            NOW,
        )
        self.assertFalse(due)
        self.assertEqual(next_due, NOW + timedelta(hours=1))

    def test_exactly_24_hours_is_due(self):
        due, _, _ = backup.due_status(
            self.state(timedelta(hours=24)),
            self.DESTINATION,
            24,
            NOW,
        )
        self.assertTrue(due)

    def test_changed_destination_is_due(self):
        state = backup.BackupState(
            NOW,
            "/Volumes/Other/vq-memgraph",
            "bundle",
        )
        due, _, _ = backup.due_status(
            state, self.DESTINATION, 24, NOW
        )
        self.assertTrue(due)


class RunBackupTest(unittest.TestCase):
    def test_force_bypasses_local_and_remote_interval_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = backup.Config(
                smb_url="smb://Junkyard/Backup",
                mount_point=root,
                backup_subdir=backup.PurePosixPath("vq-memgraph"),
                minimum_interval_hours=24,
                container_name="vq-memgraph-mage",
                mount_timeout_seconds=30,
                command_timeout_seconds=900,
            )
            state_path = root / "state.json"
            lock_path = root / "backup.lock"
            backup.write_state(
                state_path,
                backup.BackupState(NOW, str(config.destination), "existing"),
            )
            created = backup.BackupState(
                NOW,
                str(config.destination),
                "forced",
            )
            with (
                mock.patch.object(backup, "utc_now", return_value=NOW),
                mock.patch.object(
                    backup,
                    "ensure_smb_mount",
                    return_value=False,
                ),
                mock.patch.object(backup, "latest_remote_state") as remote,
                mock.patch.object(
                    backup,
                    "create_bundle",
                    return_value=created,
                ) as create,
            ):
                result = backup.run_backup(
                    config,
                    state_path,
                    lock_path,
                    force=True,
                )

            self.assertEqual(result, 0)
            remote.assert_not_called()
            create.assert_called_once_with(config, NOW, forced=True)
            self.assertEqual(backup.read_state(state_path).bundle, "forced")

    def test_parser_accepts_force_mode(self):
        args = backup.parser().parse_args(["--force"])
        self.assertTrue(args.force)


class DumpTest(unittest.TestCase):
    def test_complete_dump_is_measured(self):
        lines = [
            "CREATE (:__mg_vertex__:`Func` {__mg_id__: 1});\n",
            "CREATE (:__mg_vertex__:`Reg` {__mg_id__: 2});\n",
            "CREATE INDEX ON :__mg_vertex__(__mg_id__);\n",
            (
                "MATCH (u:__mg_vertex__), (v:__mg_vertex__) "
                "WHERE u.__mg_id__ = 1 AND v.__mg_id__ = 2 "
                "CREATE (u)-[:`USES`]->(v);\n"
            ),
            "DROP INDEX ON :__mg_vertex__(__mg_id__);\n",
            "MATCH (u) REMOVE u:__mg_vertex__, u.__mg_id__;\n",
            "CREATE INDEX ON :`Func`(`addr`);\n",
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "database.cypherl.gz"
            with gzip.open(path, "wt", encoding="utf-8") as fh:
                fh.writelines(lines)
            stats = backup.inspect_dump(path)
        self.assertEqual(stats.nodes, 2)
        self.assertEqual(stats.relationships, 1)
        self.assertEqual(stats.indexes, 1)
        self.assertEqual(stats.lines, len(lines))

    def test_truncated_dump_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "database.cypherl.gz"
            with gzip.open(path, "wt", encoding="utf-8") as fh:
                fh.write("CREATE (:__mg_vertex__:`Func` {__mg_id__: 1});\n")
            with self.assertRaisesRegex(backup.BackupError, "relationships"):
                backup.inspect_dump(path)


class RemoteStateTest(unittest.TestCase):
    def test_latest_complete_bundle_is_selected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, created in (
                ("older", "2026-07-22T03:00:00Z"),
                ("newer", "2026-07-23T03:00:00Z"),
            ):
                bundle = root / name
                bundle.mkdir()
                (bundle / "database.cypherl.gz").touch()
                (bundle / "manifest.json").write_text(
                    json.dumps({
                        "format_version": backup.FORMAT_VERSION,
                        "created_at_utc": created,
                        "files": {"database.cypherl.gz": {}},
                    }),
                    encoding="utf-8",
                )
            partial = root / ".partial"
            partial.mkdir()
            (partial / "database.cypherl.gz").touch()
            (partial / "manifest.json").write_text(
                json.dumps({
                    "format_version": backup.FORMAT_VERSION,
                    "created_at_utc": "2026-07-24T03:00:00Z",
                    "files": {"database.cypherl.gz": {}},
                }),
                encoding="utf-8",
            )
            state = backup.latest_remote_state(root)
        self.assertEqual(state.bundle, "newer")
        self.assertEqual(
            state.created_at,
            datetime(2026, 7, 23, 3, 0, tzinfo=timezone.utc),
        )


class MountTest(unittest.TestCase):
    def test_source_with_user_is_parsed(self):
        record = (
            "//rudoy@Junkyard/Backup on /Volumes/Backup "
            "(smbfs, nodev, nosuid)"
        )
        host, share = backup.mount_source(record)
        self.assertEqual(host, "junkyard")
        self.assertEqual(share, "Backup")


class SnapshotTest(unittest.TestCase):
    def output(self):
        return (
            '"path","timestamp","creation_time","size"\n'
            '"/var/lib/memgraph/snapshots/older","10",'
            '"2026-07-24T01:00:00+0000","1MiB"\n'
            '"/var/lib/memgraph/snapshots/newer","20",'
            '"2026-07-24T02:00:00+0000","1MiB"\n'
        )

    def test_newest_snapshot_is_selected(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshots = Path(directory)
            (snapshots / "newer").touch()
            selected = backup.parse_snapshot_output(self.output(), snapshots)
        self.assertEqual(selected.host_path.name, "newer")
        self.assertEqual(selected.timestamp, 20)

    def test_create_and_show_use_separate_mgconsole_calls(self):
        config = backup.Config(
            smb_url="smb://Junkyard/Backup",
            mount_point=Path("/Volumes/Backup"),
            backup_subdir=backup.PurePosixPath("vq-memgraph"),
            minimum_interval_hours=24,
            container_name="vq-memgraph-mage",
            mount_timeout_seconds=30,
            command_timeout_seconds=900,
        )
        with tempfile.TemporaryDirectory() as directory:
            snapshots = Path(directory)
            (snapshots / "newer").touch()
            with (
                mock.patch.object(backup, "SNAPSHOT_DIR", snapshots),
                mock.patch.object(
                    backup,
                    "docker_mgconsole",
                    side_effect=["", self.output()],
                ) as mgconsole,
            ):
                selected = backup.create_snapshot(config)
        self.assertEqual(selected.host_path.name, "newer")
        self.assertEqual(
            [call.args[1] for call in mgconsole.call_args_list],
            ["CREATE SNAPSHOT;\n", "SHOW SNAPSHOTS;\n"],
        )


class BundleTest(unittest.TestCase):
    def test_bundle_is_published_after_validation(self):
        dump_lines = [
            "CREATE (:__mg_vertex__:`Func` {__mg_id__: 1});\n",
            "CREATE (:__mg_vertex__:`Reg` {__mg_id__: 2});\n",
            "CREATE INDEX ON :__mg_vertex__(__mg_id__);\n",
            (
                "MATCH (u:__mg_vertex__), (v:__mg_vertex__) "
                "WHERE u.__mg_id__ = 1 AND v.__mg_id__ = 2 "
                "CREATE (u)-[:`USES`]->(v);\n"
            ),
            "DROP INDEX ON :__mg_vertex__(__mg_id__);\n",
            "MATCH (u) REMOVE u:__mg_vertex__, u.__mg_id__;\n",
            "CREATE INDEX ON :`Func`(`addr`);\n",
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_snapshot = root / "snapshot.source"
            source_snapshot.write_bytes(b"snapshot")
            config = backup.Config(
                smb_url="smb://Junkyard/Backup",
                mount_point=root,
                backup_subdir=backup.PurePosixPath("vq-memgraph"),
                minimum_interval_hours=24,
                container_name="vq-memgraph-mage",
                mount_timeout_seconds=30,
                command_timeout_seconds=900,
            )

            def write_dump(_config, path):
                with gzip.open(path, "wt", encoding="utf-8") as fh:
                    fh.writelines(dump_lines)

            snapshot = backup.Snapshot(
                source_snapshot,
                "/var/lib/memgraph/snapshots/snapshot.source",
                10,
                "2026-07-24T03:00:00+0000",
            )
            with (
                mock.patch.object(
                    backup, "require_smb_mount", return_value="//server/share"
                ),
                mock.patch.object(
                    backup, "container_image", return_value="memgraph:test"
                ),
                mock.patch.object(
                    backup, "create_snapshot", return_value=snapshot
                ),
                mock.patch.object(backup, "stream_dump", side_effect=write_dump),
                mock.patch.object(
                    backup,
                    "git_metadata",
                    return_value={
                        "head": "a" * 40,
                        "branch": "main",
                        "dirty": False,
                        "status_sha256": "b" * 64,
                    },
                ),
            ):
                state = backup.create_bundle(config, NOW)

            bundle = config.destination / state.bundle
            manifest = json.loads(
                (bundle / "manifest.json").read_text(encoding="utf-8")
            )
            self.assertTrue((bundle / "database.cypherl.gz").is_file())
            self.assertTrue((bundle / "snapshot" / "snapshot.source").is_file())
            self.assertEqual(manifest["database"]["nodes"], 2)
            self.assertEqual(manifest["database"]["relationships"], 1)
            self.assertFalse(manifest["forced"])
            self.assertFalse(any(
                child.name.startswith(".") for child in config.destination.iterdir()
            ))


if __name__ == "__main__":
    unittest.main()
