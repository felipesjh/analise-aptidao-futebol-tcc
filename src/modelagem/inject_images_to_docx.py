import zipfile
import os
import shutil
import xml.etree.ElementTree as ET

def inject_images():
    src_docx = '../[Trabalho Final v2] - Felipe  Santos De Jesus.docx'
    out_docx1 = '../[Trabalho Final] - Felipe  Santos De Jesus.docx'
    out_docx2 = '../[Trabalho Final v2] - Felipe  Santos De Jesus.docx'
    
    scratch_dir = 'scratch_docx_img'
    if os.path.exists(scratch_dir):
        shutil.rmtree(scratch_dir)
    os.makedirs(scratch_dir, exist_ok=True)
    
    with zipfile.ZipFile(src_docx, 'r') as z:
        z.extractall(scratch_dir)
        
    media_dir = os.path.join(scratch_dir, 'word', 'media')
    os.makedirs(media_dir, exist_ok=True)
    
    # Copy images to word/media/
    img_files = {
        "img_comp": ("app/assets/grafico_comparativo_modelos.png", "image_comp.png", "rIdCompChart"),
        "img_cm_raw": ("app/assets/cm_raw_logreg.png", "image_cm_raw.png", "rIdCmRaw"),
        "img_cm_fw": ("app/assets/cm_norm_atacante.png", "image_cm_fw.png", "rIdCmFw"),
        "img_cm_gk": ("app/assets/cm_norm_goleiro.png", "image_cm_gk.png", "rIdCmGk")
    }
    
    for key, (src, target_filename, r_id) in img_files.items():
        if os.path.exists(src):
            shutil.copy(src, os.path.join(media_dir, target_filename))
            print(f"Copiado {src} -> word/media/{target_filename}")
            
    # Update word/_rels/document.xml.rels
    rels_path = os.path.join(scratch_dir, 'word', '_rels', 'document.xml.rels')
    tree_rels = ET.parse(rels_path)
    root_rels = tree_rels.getroot()
    
    ns_rel = 'http://schemas.openxmlformats.org/package/2006/relationships'

    for key, (src, target_filename, r_id) in img_files.items():
        # Check if r_id exists
        existing = False
        for rel in root_rels.findall(f'{{{ns_rel}}}Relationship'):
            if rel.attrib.get('Id') == r_id:
                existing = True
                break
        if not existing:
            rel_elem = ET.SubElement(root_rels, f'{{{ns_rel}}}Relationship')
            rel_elem.attrib['Id'] = r_id
            rel_elem.attrib['Type'] = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'
            rel_elem.attrib['Target'] = f'media/{target_filename}'
            
    tree_rels.write(rels_path, xml_declaration=True, encoding='utf-8')
    print("Atualizado word/_rels/document.xml.rels com os relacionamentos de imagens!")

    # Helper to generate OpenXML <w:drawing> for image
    def create_image_drawing_elem(r_id, width_emu=5715000, height_emu=3302000, doc_id=1, name="Gráfico"):
        # 5715000 EMU = ~6.25 inches wide, 3302000 EMU = ~3.6 inches high
        drawing_xml = f'''<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
  <w:pPr>
    <w:jc w:val="center"/>
  </w:pPr>
  <w:r>
    <w:drawing>
      <wp:inline distT="0" distB="0" distL="0" distR="0">
        <wp:extent cx="{width_emu}" cy="{height_emu}"/>
        <wp:effectExtent l="0" t="0" r="0" b="0"/>
        <wp:docPr id="{doc_id}" name="{name}"/>
        <wp:cNvGraphicFramePr>
          <a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/>
        </wp:cNvGraphicFramePr>
        <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
          <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
            <pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
              <pic:nvPicPr>
                <pic:cNvPr id="{doc_id}" name="{name}"/>
                <pic:cNvPicPr/>
              </pic:nvPicPr>
              <pic:blipFill>
                <a:blip r:embed="{r_id}"/>
                <a:stretch>
                  <a:fillRect/>
                </a:stretch>
              </pic:blipFill>
              <pic:spPr>
                <a:xfrm>
                  <a:off x="0" y="0"/>
                  <a:ext cx="{width_emu}" cy="{height_emu}"/>
                </a:xfrm>
                <a:prstGeom prst="rect">
                  <a:avLst/>
                </a:prstGeom>
              </pic:spPr>
            </pic:pic>
          </a:graphicData>
        </a:graphic>
      </wp:inline>
    </w:drawing>
  </w:r>
</w:p>'''
        return ET.fromstring(drawing_xml)

    # Insert drawings into document.xml
    doc_path = os.path.join(scratch_dir, 'word', 'document.xml')
    tree_doc = ET.parse(doc_path)
    root_doc = tree_doc.getroot()
    body = root_doc.find('w:body', {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})
    
    # Locate where to insert the comparison chart image
    for i, elem in enumerate(body):
        texts = ''.join([t.text for t in elem.findall('.//w:t', {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}) if t.text])
        if 'Resultados Finais dos Modelos Normalizados' in texts:
            print(f"Inserindo Gráfico Comparativo de Modelos no índice {i+1}")
            img_p = create_image_drawing_elem("rIdCompChart", width_emu=5400000, height_emu=3120000, doc_id=101, name="Gráfico Comparativo")
            body.insert(i+1, img_p)
            break
            
    # Locate where to insert raw logreg confusion matrix image
    for i, elem in enumerate(body):
        texts = ''.join([t.text for t in elem.findall('.//w:t', {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}) if t.text])
        if 'Diagnóstico Numérico dos Modelos Iniciais Sem Normalização' in texts:
            print(f"Inserindo Matriz Sem Normalização no índice {i+2}")
            img_raw = create_image_drawing_elem("rIdCmRaw", width_emu=4800000, height_emu=3840000, doc_id=102, name="Matriz Raw")
            body.insert(i+2, img_raw)
            break

    # Save document.xml
    tree_doc.write(doc_path, xml_declaration=True, encoding='utf-8')
    
    # Repack docx
    for target in [out_docx1, out_docx2]:
        with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z_out:
            for foldername, subfolders, filenames in os.walk(scratch_dir):
                for filename in filenames:
                    filepath = os.path.join(foldername, filename)
                    arcname = os.path.relpath(filepath, scratch_dir)
                    z_out.write(filepath, arcname)
        print(f"DOCX atualizado com imagens incorporadas: {target}")

if __name__ == '__main__':
    inject_images()
