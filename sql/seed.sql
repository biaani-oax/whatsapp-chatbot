
INSERT INTO company_knowledge
    (knowledge_key, category, content)
VALUES
    (
        'nombre',
        'general',
        'Biaani STEAM Maker Space'
    ),
    (
        'descripcion',
        'general',
        'Espacio de aprendizaje STEM, maker y desarrollo de proyectos.'
    ),
    (
        'servicios',
        'servicios',
        'Robótica, programación, matemáticas, impresión 3D y talleres.'
    ),
    (
        'modalidad',
        'general',
        'Actividades para niños, jóvenes y adultos.'
    )
ON CONFLICT (knowledge_key) DO NOTHING;
