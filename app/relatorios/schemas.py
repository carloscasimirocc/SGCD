'''
Serializadores Marshmallow para os relatórios.
Normalizam dicts/iterables vindos dos services para listas/dicts JSON-serializáveis.
'''
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple, Union, cast

from marshmallow import Schema, fields

Number = Union[int, float, Decimal]


class MensalItemSchema(Schema):
    mes = fields.Int(required=True)
    total = fields.Float(required=True)


class TrimestralItemSchema(Schema):
    trimestre = fields.Int(required=True)
    total = fields.Float(required=True)


class ResumoSchema(Schema):
    total = fields.Float(allow_none=True)
    media = fields.Float(allow_none=True)
    maior = fields.Float(allow_none=True)
    menor = fields.Float(allow_none=True)


def _to_float_safe(value: Optional[Number]) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _normalize_dict_to_list(raw: Mapping[Any, Number], key_name: str) -> List[Dict[str, Any]]:
    '''
    Converte um mapping {key: number} em lista ordenada
    [{key_name: int, 'total': float}, ...]
    Aceita keys não-inteiras (converte com int()).
    '''
    items: List[Tuple[int, Number]] = []
    for k, v in raw.items():
        try:
            ik = int(k)
        except Exception:
            # fallback: tentar converter string numérica, senão colocar 0
            try:
                ik = int(float(str(k)))
            except Exception:
                ik = 0
        items.append((ik, v))
    items.sort(key=lambda t: t[0])
    return [{key_name: int(k), 'total': _to_float_safe(v)} for k, v in items]


def serialize_mensais(raw: Any) -> List[Dict[str, Any]]:
    '''Normaliza e serializa totais mensais para lista de dicts {'mes', 'total'}.'''
    if not raw:
        return []
    if isinstance(raw, Mapping):
        # assume {mes: total}
        data = _normalize_dict_to_list(raw, 'mes')
    else:
        # assume iterable of mapping-like items
        data: List[Dict[str, Any]] = []
        for item in raw:
            if not isinstance(item, Mapping):
                continue
            mes = item.get('mes') or item.get('month') or item.get('key')
            total = item.get('total') or item.get('value')
            if mes is None:
                continue
            try:
                imes = int(mes)
            except Exception:
                try:
                    imes = int(float(str(mes)))
                except Exception:
                    continue
            data.append({'mes': imes, 'total': _to_float_safe(total)})
    return cast(List[Dict[str, Any]], MensalItemSchema(many=True).dump(data))


def serialize_trimestrais(raw: Any) -> List[Dict[str, Any]]:
    '''Normaliza e serializa totais trimestrais para lista de dicts {'trimestre', 'total'}.'''
    if not raw:
        return []
    if isinstance(raw, Mapping):
        data = _normalize_dict_to_list(raw, 'trimestre')
    else:
        data = []
        for item in raw:
            if not isinstance(item, Mapping):
                continue
            tri = item.get('trimestre') or item.get(
                'quarter') or item.get('key')
            total = item.get('total') or item.get('value')
            if tri is None:
                continue
            try:
                itri = int(tri)
            except Exception:
                try:
                    itri = int(float(str(tri)))
                except Exception:
                    continue
            data.append({'trimestre': itri, 'total': _to_float_safe(total)})
    return cast(List[Dict[str, Any]], TrimestralItemSchema(many=True).dump(data))


def serialize_resumo(raw: Any) -> Dict[str, Any]:
    '''Normaliza e serializa resumo estatístico para um dict com floats.'''
    if not raw:
        return cast(Dict[str, Any], ResumoSchema().dump(
            {'total': 0.0, 'media': 0.0, 'maior': 0.0, 'menor': 0.0}
        ))
    if isinstance(raw, Mapping):
        prepared = {
            'total': _to_float_safe(raw.get('total')),
            'media': _to_float_safe(raw.get('media')),
            'maior': _to_float_safe(raw.get('maior')),
            'menor': _to_float_safe(raw.get('menor')),
        }
    else:
        prepared = {
            'total': _to_float_safe(getattr(raw, 'total', None)),
            'media': _to_float_safe(getattr(raw, 'media', None)),
            'maior': _to_float_safe(getattr(raw, 'maior', None)),
            'menor': _to_float_safe(getattr(raw, 'menor', None)),
        }
    return cast(Dict[str, Any], ResumoSchema().dump(prepared))
