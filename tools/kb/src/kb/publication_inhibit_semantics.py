"""Separate calibration, filter and conditional publication equations."""


def lookup(table,rpm):
    if (type(table) is not bytes or len(table)!=4 or type(rpm) is not int
            or not 0<=rpm<=65535):
        raise ValueError('the inhibit lookup needs its four unsigned cells and RPM word')
    coordinate=max(0,min(255,rpm-96))
    if coordinate>=192:
        return dict(coordinate=coordinate,output=table[3],operand_offsets=[3])
    index,remainder=divmod(coordinate,64)
    first,second=table[index:index+2]
    amount=abs(second-first)*remainder//64
    value=first+amount if second>=first else first-amount
    return dict(coordinate=coordinate,output=value,operand_offsets=[index,index+1])


def filtered(image,before,fault):
    if fault:
        return image[0x84A3]<<8
    previous=int.from_bytes(before[0x1F76:0x1F78],'big')
    current=int.from_bytes(before[0x114A:0x114C],'big')
    if not before[0x24B8]&64 or previous<current:return 0
    coefficient=image[0x84A4]
    history=int.from_bytes(before[0x1E58:0x1E5A],'big')
    return min(((previous-current)*coefficient*256+history*(256-coefficient))//256,65535)


def publication(filtered_value,cached,mode,brake):
    if (any(type(value) is not int for value in (filtered_value,cached,mode,brake))
            or not 0<=filtered_value<=65535 or any(not 0<=value<=255 for value in (cached,mode,brake))):
        raise ValueError('the publication gate needs its exact upstream word and control bytes')
    enabled=bool(mode&32) and (cached==0 or bool(brake&128))
    return filtered_value>>8 if enabled else 0
