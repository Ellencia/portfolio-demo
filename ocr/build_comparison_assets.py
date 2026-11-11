"""Align the recognition/repair comparison without changing the OMR content.

Use one engraved layout for both states. Hide only the manually added last
note for the before state, leaving the staff and the first six notes fixed.
The source MusicXML and its recognition errors remain untouched.
"""
import copy
import xml.etree.ElementTree as ET
from pathlib import Path

IMG = Path(__file__).resolve().parent.parent / 'img'
NS = {'s': 'http://www.w3.org/2000/svg'}


def build():
    before = ET.parse(IMG / 'ocr_edit_before.musicxml').getroot()
    repaired = ET.parse(IMG / 'ocr_repair_example.musicxml').getroot()
    original_notes = before.findall('.//note')
    repair_notes = repaired.findall('.//note')
    assert len(original_notes) == 6 and len(repair_notes) == 7
    assert all(ET.tostring(a) == ET.tostring(b)
               for a, b in zip(original_notes, repair_notes))

    root = ET.parse(IMG / 'ocr_repair_example.svg').getroot()
    root.set('width', '300px')
    root.set('height', '90px')
    root.find('s:svg', NS).set('viewBox', '400 650 5000 1500')
    # The cropped comparison has no need for the standalone measure number.
    for parent in root.iter():
        for child in list(parent):
            if 'mNum' in child.get('class', '').split():
                parent.remove(child)
    ET.register_namespace('', NS['s'])
    ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
    for state in ('before', 'after'):
        image = copy.deepcopy(root)
        if state == 'before':
            notes = image.findall('.//s:g[@class="note"]', NS)
            assert len(notes) == 7
            added = notes[-1]
            parent = next(e for e in image.iter() if added in list(e))
            parent.remove(added)
        (IMG / f'ocr_compare_{state}.svg').write_text(
            ET.tostring(image, encoding='unicode'), encoding='utf-8')


if __name__ == '__main__':
    build()
    print('Built aligned comparison: same staff and six notes, one added note.')
