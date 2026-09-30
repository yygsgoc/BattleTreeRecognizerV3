from enum import IntFlag

import comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0 as __wrapper_module__
from comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0 import (
    StdPicture, Picture, Unchecked, FontEvents, Default, IPictureDisp,
    OLE_YPOS_CONTAINER, BSTR, IUnknown, IFont, typelib_path,
    IFontEventsDisp, _check_version, OLE_YPOS_PIXELS,
    OLE_YSIZE_HIMETRIC, OLE_COLOR, OLE_XPOS_HIMETRIC, _lcid, VgaColor,
    Color, StdFont, OLE_XPOS_CONTAINER, VARIANT_BOOL,
    OLE_ENABLEDEFAULTBOOL, IPicture, DISPMETHOD, OLE_YPOS_HIMETRIC,
    OLE_YSIZE_PIXELS, GUID, Font, EXCEPINFO, FONTITALIC, FONTBOLD,
    OLE_YSIZE_CONTAINER, DISPPROPERTY, Gray, OLE_XSIZE_PIXELS,
    FONTSIZE, CoClass, OLE_OPTEXCLUSIVE, OLE_XPOS_PIXELS, dispid,
    OLE_CANCELBOOL, Monochrome, FONTUNDERSCORE, Library,
    OLE_XSIZE_HIMETRIC, FONTSTRIKETHROUGH, COMMETHOD, DISPPARAMS,
    IFontDisp, IEnumVARIANT, FONTNAME, IDispatch, HRESULT, Checked,
    OLE_XSIZE_CONTAINER, OLE_HANDLE
)


class OLE_TRISTATE(IntFlag):
    Unchecked = 0
    Checked = 1
    Gray = 2


class LoadPictureConstants(IntFlag):
    Default = 0
    Monochrome = 1
    VgaColor = 2
    Color = 4


__all__ = [
    'FONTITALIC', 'StdPicture', 'FONTBOLD', 'Picture', 'Unchecked',
    'FontEvents', 'OLE_YSIZE_CONTAINER', 'Default', 'Gray',
    'IPictureDisp', 'OLE_XSIZE_PIXELS', 'FONTSIZE',
    'LoadPictureConstants', 'OLE_YPOS_CONTAINER', 'OLE_OPTEXCLUSIVE',
    'OLE_XPOS_PIXELS', 'IFont', 'typelib_path', 'IFontEventsDisp',
    'OLE_CANCELBOOL', 'Monochrome', 'FONTUNDERSCORE',
    'OLE_YPOS_PIXELS', 'OLE_YSIZE_HIMETRIC', 'OLE_COLOR',
    'OLE_XPOS_HIMETRIC', 'VgaColor', 'Library', 'OLE_XSIZE_HIMETRIC',
    'Color', 'StdFont', 'FONTSTRIKETHROUGH', 'OLE_XPOS_CONTAINER',
    'OLE_ENABLEDEFAULTBOOL', 'IPicture', 'IFontDisp', 'FONTNAME',
    'OLE_TRISTATE', 'OLE_YPOS_HIMETRIC', 'OLE_YSIZE_PIXELS', 'Font',
    'Checked', 'OLE_XSIZE_CONTAINER', 'OLE_HANDLE'
]

