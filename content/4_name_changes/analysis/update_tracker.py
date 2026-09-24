"""Update only DC004, preserving the tracker's other rows and UTF-8 BOM."""
import csv,io
from pathlib import Path
post=Path(__file__).resolve().parents[1]
path=post.parent/'datacuse-story-tracker.csv'
raw=path.read_bytes()
text=raw.decode('utf-8-sig');lines=text.splitlines(keepends=True)
header=next(csv.reader([lines[0]]))
assert len(header)==11
matched=[]
for i,line in enumerate(lines[1:],1):
    row=next(csv.reader([line]))
    if row[0]!='DC004':continue
    assert len(row)==11
    record=dict(zip(header,row))
    record.update({'Status':'Ready','Research Notes':'Revised draft distinguishes whole-path straightness from continuity. Among 218 defined windows, max 2 changes with <=10 m chord departure and <=1% extra distance, 50 m lead-in/out. Monticello South-North-Springbrook: 686.8 m, 0.20% extra, 7.1 m departure; names agree with city map. Tennyson-Burnet Park-Tennyson ties in NYS but city map calls the insert Tennyson. Original 4-change chains curve substantially. 642 geometry windows independently validated; 12 aerial transitions checked; three new graphics. Bounded chain/window search, not a universal record. Unpublished.',
        'Sources':'NYS Streets and NYS city boundaries, saved 2026-09-19 snapshot; NYS 2022 aerial imagery; analysis/methodology.md',
        'Draft Location':str(post/'story'/'index.md')})
    out=io.StringIO(newline='');writer=csv.writer(out,quoting=csv.QUOTE_ALL,lineterminator='\r\n')
    writer.writerow([record[k] for k in header]);lines[i]=out.getvalue();matched.append(i)
assert len(matched)==1
path.write_bytes(b'\xef\xbb\xbf'+''.join(lines).encode('utf-8'))
print('Updated DC004 to Ready; article stays draft.')
