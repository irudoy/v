"""Exact registered width families; unrelated or failed proofs retain raw questions."""

from kb import packed_width, width_view_resolution


def registered_field(root,symbol):
    fields=[row for row in packed_width.contract.descriptor(root)['field'] if row['symbol']==symbol]
    other=width_view_resolution.registered_field(root,symbol)
    if other is not None:
        fields.append(other)
    if len(fields)>1:
        raise ValueError('the native width question belongs to more than one proof family')
    return fields[0] if fields else None


def family(root,symbol):
    packed=any(row['symbol']==symbol for row in packed_width.contract.descriptor(root)['field'])
    views=width_view_resolution.registered_field(root,symbol) is not None
    if packed==views:
        raise ValueError('the native width question has no unique exact proof family')
    return packed_width if packed else width_view_resolution


def require(model,symbol,claim):
    return family(model.root,symbol.key.key).require(model,symbol,claim)


def accepted(model,symbol,claim):
    try:
        return family(model.root,symbol.key.key).accepted(model,symbol,claim)
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,IndexError,RecursionError):
        return None
