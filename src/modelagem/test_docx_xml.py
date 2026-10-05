import zipfile
import os
import xml.etree.ElementTree as ET

def test_xml_edit():
    src_docx = '../[Trabalho Final] - Felipe  Santos De Jesus.docx'
    out_docx = '../[Trabalho Final] - Felipe  Santos De Jesus.docx'
    out_v2_docx = '../[Trabalho Final v2] - Felipe  Santos De Jesus.docx'
    
    # Extract to scratch
    scratch_dir = 'scratch_docx'
    os.makedirs(scratch_dir, exist_ok=True)
    
    with zipfile.ZipFile(src_docx, 'r') as z:
        z.extractall(scratch_dir)
        
    doc_path = os.path.join(scratch_dir, 'word', 'document.xml')
    tree = ET.parse(doc_path)
    root = tree.getroot()
    
    print("Root tag:", root.tag)
    
    # Save back to zip
    with zipfile.ZipFile(out_docx, 'w', zipfile.ZIP_DEFLATED) as z_out:
        for foldername, subfolders, filenames in os.walk(scratch_dir):
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                arcname = os.path.relpath(filepath, scratch_dir)
                z_out.write(filepath, arcname)
                
    print("Successfully created test updated docx:", out_docx)

if __name__ == '__main__':
    test_xml_edit()
