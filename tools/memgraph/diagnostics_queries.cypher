// Diagnostic catalog query examples.
// Every semantic claim remains connected to its exact source fragment.

// DTC inventory in each ROM and exact-manual semantic coverage.
MATCH (rom:Rom)<-[:IN_ROM]-(descriptor:RomDtcDescriptor)-[:ENCODES]->(code:DtcCode)
WITH rom, count(descriptor) AS descriptors, count(DISTINCT code) AS unique_codes,
     collect(DISTINCT code) AS codes
UNWIND codes AS code
OPTIONAL MATCH (definition:DtcDefinition)-[:DEFINES]->(code)
WITH rom, descriptors, unique_codes,
     count(DISTINCT CASE
       WHEN definition.applicability_status = 'exact_manual'
        AND definition.ecu_id ENDS WITH ':ecm' THEN code END
     ) AS exact_manual_codes
RETURN rom.id AS rom, descriptors, unique_codes, exact_manual_codes,
       toFloat(exact_manual_codes) * 100.0 / unique_codes AS exact_manual_percent
ORDER BY rom;

// All evidence for one DTC, grouped by claim type and source.
MATCH (code:DtcCode {code:'P0605'})
OPTIONAL MATCH (descriptor:RomDtcDescriptor)-[:ENCODES]->(code)
OPTIONAL MATCH (descriptor)-[:IN_ROM]->(rom:Rom)
WITH code,
     collect(DISTINCT CASE WHEN descriptor IS NULL THEN null ELSE {
       rom:rom.id, index:descriptor.index, record_addr:descriptor.record_addr,
       attribute_addr:descriptor.attribute_addr,
       attribute_hex:descriptor.attribute_hex
     } END) AS descriptors
OPTIONAL MATCH (definition:DtcDefinition)-[:DEFINES]->(code)
OPTIONAL MATCH (definition)-[:RESTS_ON]->(fragment:SourceFragment)
WITH code, descriptors,
     collect(DISTINCT CASE WHEN definition IS NULL THEN null ELSE {
       title:definition.title, native_code:definition.native_code,
       ecu_id:definition.ecu_id, dataset_id:definition.dataset_id,
       document_id:fragment.document_id, pdf_page:fragment.pdf_page,
       page_label:fragment.page_label
     } END) AS definitions
OPTIONAL MATCH (detail:SourceFragment)-[:DESCRIBES_DTC]->(code)
WHERE detail.kind = 'dtc_detail'
RETURN code.code AS code, descriptors, definitions,
       collect(DISTINCT CASE WHEN detail IS NULL THEN null ELSE {
         heading:detail.heading, dataset_id:detail.dataset_id,
         document_id:detail.document_id, pdf_page:detail.pdf_page,
         page_label:detail.page_label,
         primary:toUpper(coalesce(detail.heading, '')) CONTAINS code.code
       } END) AS details;

// Nissan SID 0x22 interpretations with requests isolated to their datasets.
MATCH (definition:ParameterDefinition)-[:DEFINES]->(parameter:DiagnosticParameter)
WHERE definition.request_hex = '221201'
OPTIONAL MATCH (request:DiagnosticRequest)-[:RETURNS]->(parameter)
WHERE request.dataset_id = definition.dataset_id
OPTIONAL MATCH (definition)-[:RESTS_ON]->(fragment:SourceFragment)
OPTIONAL MATCH (request)-[:RESTS_ON]->(request_fragment:SourceFragment)
WITH definition, fragment,
     collect(DISTINCT CASE WHEN request IS NULL THEN null ELSE {
       id:request.id, request_hex:request.request_hex,
       dataset_id:request.dataset_id,
       document_id:request_fragment.document_id
     } END) AS requests
RETURN definition.name, definition.formula, definition.factor,
       definition.addend, definition.unit, definition.verification_status,
       definition.dataset_id, fragment.document_id, requests
ORDER BY definition.dataset_id;

// Candidate claims for conflict analysis.
// query.py normalizes affine formulas and unit aliases before reporting a conflict.
MATCH (request:DiagnosticRequest)-[:RETURNS]->(parameter:DiagnosticParameter)
      <-[:DEFINES]-(definition:ParameterDefinition)
WHERE request.service_id = '0x22'
  AND coalesce(request.request_hex, '') <> ''
  AND (definition.formula IS NOT NULL OR definition.factor IS NOT NULL)
WITH DISTINCT request.request_hex AS request_hex, definition
WITH request_hex,
     collect(DISTINCT {
       dataset_id:definition.dataset_id, name:definition.name,
       formula:definition.formula, factor:definition.factor,
       addend:definition.addend, unit:definition.unit
     }) AS definitions
RETURN request_hex, definitions
ORDER BY request_hex;

// CAN route definitions and physical bindings remain separate evidence groups.
MATCH (signal:CanSignal)
WHERE toLower(signal.name) CONTAINS 'vehicle speed'
OPTIONAL MATCH (definition:CanSignalDefinition)-[:DEFINES]->(signal)
OPTIONAL MATCH (definition)-[:TRANSMITTER]->(transmitter:Ecu)
OPTIONAL MATCH (definition)-[:RECEIVER]->(receiver:Ecu)
OPTIONAL MATCH (definition)-[:RESTS_ON]->(fragment:SourceFragment)
WITH signal, definition, fragment,
     collect(DISTINCT transmitter.id) AS transmitters,
     collect(DISTINCT receiver.id) AS receivers
WITH signal,
     collect(DISTINCT CASE WHEN definition IS NULL THEN null ELSE {
       id:definition.id, name:definition.name,
       vehicle_id:definition.vehicle_id, bus:definition.bus,
       can_id:definition.can_id, transmitters:transmitters,
       receivers:receivers, dataset_id:definition.dataset_id,
       document_id:fragment.document_id, pdf_page:fragment.pdf_page
     } END) AS definitions
OPTIONAL MATCH (binding:CanSignalBinding)-[:BINDS_SIGNAL]->(signal)
OPTIONAL MATCH (binding)-[:BINDS_FRAME]->(frame:CanFrame)
OPTIONAL MATCH (binding)-[:RESTS_ON]->(binding_fragment:SourceFragment)
WITH signal, definitions,
     collect(DISTINCT CASE WHEN binding IS NULL THEN null ELSE {
         id:binding.id, vehicle_id:coalesce(binding.vehicle_id, frame.vehicle_id),
         bus:coalesce(binding.bus, frame.bus), can_id:frame.can_id,
         byte_offset:binding.byte_offset, bit_offset:binding.bit_offset,
         bit_length:binding.bit_length, byte_order:binding.byte_order,
         factor:binding.factor, addend:binding.addend, unit:binding.unit,
         verification:binding.verification_status,
         dataset_id:binding.dataset_id,
         document_id:binding_fragment.document_id,
         pdf_page:binding_fragment.pdf_page
       } END) AS bindings
RETURN signal.name, definitions, bindings
ORDER BY signal.name;

// Active Test and Work Support definitions are data only.
MATCH (operation:DiagnosticOperation)
WHERE operation.kind IN ['active_test', 'work_support']
RETURN operation.name, operation.kind, operation.ecu_id,
       operation.description, operation.conditions, operation.usage,
       operation.executable, operation.dataset_id
ORDER BY operation.ecu_id, operation.kind, operation.name;

// Reviewed firmware targets associated with one exact DTC.
MATCH (binding:DiagnosticBinding {rom:'JK08A'})
      -[:BINDS_DIAGNOSTIC]->(:DtcCode {code:'P0327'})
MATCH (binding)-[:BINDS_FIRMWARE]->(firmware)
MATCH (binding)-[:RESTS_ON {role:'diagnostic_source'}]->(source_claim)
RETURN binding.kind, labels(firmware) AS firmware_labels,
       firmware.addr AS firmware_addr, binding.confidence,
       binding.applicability, binding.priority,
       labels(source_claim) AS source_labels,
       source_claim.id AS source_claim_id
ORDER BY binding.priority DESC, firmware_addr;

// Per-ROM static binding coverage. Confidence and source applicability remain
// independent dimensions and must not be collapsed into one rank.
MATCH (binding:DiagnosticBinding)
RETURN binding.rom, binding.kind, binding.confidence,
       binding.applicability, count(*) AS claims
ORDER BY binding.rom, binding.kind, binding.confidence,
         binding.applicability;

// Exact-ROM DTC claims must not cross the JK08A -> JK03A exact-code relation.
MATCH (binding:DiagnosticBinding {rom:'JK03A'})
      -[:BINDS_DIAGNOSTIC]->(code:DtcCode)
RETURN binding.id, code.code;
