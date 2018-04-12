
import gzip
import xml.etree.ElementTree as ET
import string

from django import template

register = template.Library()

@register.filter(name="get_informacoes")
def get_informacoes(nome):
	with gzip.open('pordesc2018-small.xml.gz') as pordesc2018:
		tree = ET.parse(pordesc2018)	

	elem = tree.find("./DescriptorRecord/*/*/*/*/[String='"+nome+"']/../../../../")
	DUI = elem.text
	descriptor = tree.find("./DescriptorRecord/[DescriptorUI='"+DUI+"']")
	name = descriptor.find('.DescriptorName/String').text
	scope = descriptor.find('.ConceptList/Concept/ScopeNote').text.replace('\n', '')

	return scope