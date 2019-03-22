# coding: utf8
from __future__ import unicode_literals, print_function, division

from pydictionaria.formats import sfm
from pydictionaria.formats import excel
from pydictionaria.formats import filemaker
from pydictionaria.formats import cldf

FORMATS = [sfm.Dictionary, excel.Dictionary, filemaker.Dictionary, cldf.Dictionary]
