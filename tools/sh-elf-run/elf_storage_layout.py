"""Reject allocated or loadable ELF32 SH storage intersecting test RAM."""
from pathlib import Path
import struct


class ELFStorageError(ValueError):
    pass


def require_separate_storage(path, ram_ranges):
    """Check both ELF sections and LOAD memory extents before simulator entry."""
    data=Path(path).read_bytes()
    if len(data)<52 or data[:7]!=b'\x7fELF\x01\x02\x01':
        raise ELFStorageError('expected big-endian ELF32')
    header=struct.unpack_from('>HHIIIIIHHHHHH',data,16)
    elf_type,machine,version,entry,phoff,shoff,flags,ehsize,phsize,phnum,shsize,shnum,shstr=header
    if machine!=42 or version!=1 or elf_type!=2 or ehsize!=52:
        raise ELFStorageError('expected executable SH ELF32 header')
    if not phnum or not shnum or phnum==65535 or shstr==65535:
        raise ELFStorageError('ordinary nonempty program and section tables required')
    if phsize!=32 or shsize!=40 or phoff<52 or shoff<52:
        raise ELFStorageError('invalid ELF table geometry')
    if phoff+phnum*phsize>len(data) or shoff+shnum*shsize>len(data):
        raise ELFStorageError('truncated ELF table')
    ranges=tuple(ram_ranges)
    if not ranges:
        raise ELFStorageError('declared RAM required')
    for begin,size in ranges:
        if type(begin) is not int or type(size) is not int or begin<0 or size<=0 or begin+size>1<<32:
            raise ELFStorageError('invalid declared RAM extent')

    def separate(kind,index,begin,size):
        if begin+size>1<<32:
            raise ELFStorageError(f'{kind}[{index}] wraps the address space')
        for ram,size_ram in ranges:
            if size and begin<ram+size_ram and ram<begin+size:
                raise ELFStorageError(
                    f'{kind}[{index}] {begin:#010x}..{begin+size:#010x} '
                    f'intersects declared RAM {ram:#010x}..{ram+size_ram:#010x}')

    allocated=loads=0
    for index in range(phnum):
        kind,offset,virtual,physical,file_size,memory_size,permissions,alignment=struct.unpack_from('>IIIIIIII',data,phoff+index*phsize)
        if kind!=1:
            continue
        loads+=1
        if file_size>memory_size or offset+file_size>len(data):
            raise ELFStorageError(f'LOAD[{index}] invalid file or memory extent')
        separate('LOAD virtual',index,virtual,memory_size)
        separate('LOAD physical',index,physical,memory_size)
    for index in range(shnum):
        name,kind,permissions,address,offset,size,link,info,alignment,entry_size=struct.unpack_from('>IIIIIIIIII',data,shoff+index*shsize)
        if not permissions&2:
            continue
        allocated+=1
        if kind!=8 and offset+size>len(data):
            raise ELFStorageError(f'ALLOC[{index}] truncated contents')
        separate('ALLOC',index,address,size)
    if not allocated or not loads:
        raise ELFStorageError('allocated sections and LOAD segments required')
    return {'allocated_sections':allocated,'load_segments':loads}
