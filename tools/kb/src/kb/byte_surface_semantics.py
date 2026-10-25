"""Independent numeric byte-surface equations, separate from raw CPU state.

Conditional wrapper geometry and calibration contents are caller inputs.
These functions establish neither natural caller reachability nor a later
conditioning/diagnostic dependency. Actual original execution is separate.
"""


def byte(value):
    if type(value) is not int or not 0<=value<=255:
        raise ValueError('the byte-surface equation requires an explicit unsigned byte')
    return value


def axis_position(axis,value):
    if (type(axis) is not bytes or len(axis) not in (4,8,16)
            or any(first>=second for first,second in zip(axis,axis[1:]))):
        raise ValueError('the byte-surface equation requires its exact monotone byte axis')
    value=byte(value)
    for index in range(len(axis)-1,-1,-1):
        if value>=axis[index]:
            if value==axis[index] or index==len(axis)-1:
                return index,0
            return index,((value-axis[index]) << 16)//(axis[index+1]-axis[index])
    return 0,0


def linear(first,second,fraction):
    first,second=byte(first),byte(second)
    if type(fraction) is not int or not 0<=fraction<65536:
        raise ValueError('the byte-surface equation requires a bounded unsigned fraction')
    amount=(abs(second-first)*fraction)//65536
    return first+amount if second>=first else first-amount


def at(table,rows,cols,row,col,row_fraction,col_fraction):
    if (type(table) is not bytes or rows not in (4,8,16) or cols not in (4,8,16)
            or len(table)!=rows*cols or type(row) is not int or type(col) is not int
            or not 0<=row<rows or not 0<=col<cols
            or any(type(value) is not int or not 0<=value<65536 for value in (row_fraction,col_fraction))
            or row==rows-1 and row_fraction!=0 or col==cols-1 and col_fraction!=0):
        raise ValueError('the byte-surface equation changes its conditional row-major extent')
    stride=cols
    first=table[row*stride+col]
    reads=[row*stride+col]
    if col_fraction:
        first=linear(first,table[row*stride+col+1],col_fraction)
        reads.append(row*stride+col+1)
    if row_fraction:
        second=table[(row+1)*stride+col]
        reads.append((row+1)*stride+col)
        if col_fraction:
            second=linear(second,table[(row+1)*stride+col+1],col_fraction)
            reads.append((row+1)*stride+col+1)
        result=linear(first,second,row_fraction)
    else:
        result=first
    raw=result if row_fraction or col_fraction or result<128 else result|0xFFFFFF00
    return dict(row=row,col=col,row_fraction=row_fraction,col_fraction=col_fraction,
                byte=result,raw=raw,reads=reads)


def surface(table,row_axis,col_axis,row_value,col_value):
    row,row_fraction=axis_position(row_axis,row_value)
    col,col_fraction=axis_position(col_axis,col_value)
    return at(table,len(row_axis),len(col_axis),row,col,row_fraction,col_fraction)


def caller(tables,axes,first_coordinate,load,force_mode,configuration,correction_mode):
    coordinate=byte(first_coordinate)
    load,force_mode,configuration,correction_mode=(byte(value) for value in
        (load,force_mode,configuration,correction_mode))
    selected=255 if force_mode&8 and configuration&1 else load
    specs=((0xB2FA,0x12EC2,0x12EA2),(0xB33A,0x12F2E,0x12F0E),(0xAB4A,0x12F96,0x12F8E))
    first=surface(tables[specs[0][0]],axes[specs[0][1]],axes[specs[0][2]],coordinate,selected)
    main=surface(tables[specs[1][0]],axes[specs[1][1]],axes[specs[1][2]],coordinate,selected)
    correction=None
    unclamped=main['byte']
    if correction_mode&64:
        correction=surface(tables[specs[2][0]],axes[specs[2][1]],axes[specs[2][2]],coordinate,selected)
        unclamped=main['byte']-correction['byte']+128
    return dict(selected_coordinate=selected,first=first,main=main,correction=correction,
        unclamped=unclamped,lower_clamp=unclamped<0,upper_clamp=unclamped>255,
        output_first=first['byte'],output_main=min(255,max(0,unclamped)),
        outputs={0xFFFF1C5F:first['byte'],0xFFFF1C5D:min(255,max(0,unclamped))})
