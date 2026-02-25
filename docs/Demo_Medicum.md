# Demo Medicum — Guia de Demostración con Claude

**Plataforma:** SuperChat (OpenCloud / Claude)
**Objetivo:** Demostrar las capacidades de un asistente IA clínico en una consulta médica real
**Duración estimada:** 15-20 minutos
**Fecha:** Febrero 2026

---

## Preparación

### Antes de empezar

1. Abre SuperChat con el modelo Claude
2. Ten este documento abierto como referencia
3. Cada bloque `📋 PROMPT` es un mensaje que copias y pegas en SuperChat
4. Espera la respuesta de Claude antes de enviar el siguiente
5. Si quieres probar con imagen, ten preparada una radiografía de rodilla (o cualquier imagen médica)

### Contexto del paciente (para toda la demo)

El paciente ficticio es:
- **Nombre:** María García López
- **Edad:** 58 años
- **Sexo:** Femenino
- **NHC:** 2024-78432
- **Antecedentes:** Diabetes tipo 2 (Metformina 850mg/12h), Hipertensión (Enalapril 20mg/día), Obesidad grado I (IMC 31.2)
- **Alergias:** Penicilina (urticaria), AINEs (broncoespasmo leve)

---

## FASE 1: Establecer el Rol del Asistente

### Paso 1.1 — Configurar a Claude como asistente clínico

📋 **PROMPT:**

```
Actúa como un asistente clínico de IA para un médico de atención primaria. Tu rol es:

1. Escuchar la información que te doy sobre la consulta con el paciente
2. Generar automáticamente la nota SOAP (Subjetivo, Objetivo, Análisis, Plan)
3. Sugerir posibles diagnósticos con códigos CIE-10
4. Recomendar pruebas diagnósticas
5. Proponer tratamientos y prescripciones con posología
6. Verificar interacciones medicamentosas con la medicación actual del paciente
7. Citar guías clínicas cuando sea relevante

Datos del paciente actual:
- María García López, 58 años, mujer
- NHC: 2024-78432
- Antecedentes: DM2 (Metformina 850mg/12h), HTA (Enalapril 20mg/día), Obesidad grado I (IMC 31.2)
- Alergias: Penicilina (urticaria), AINEs (broncoespasmo leve)
- Medicación actual: Metformina 850mg c/12h, Enalapril 20mg c/24h

Responde siempre en español médico profesional. Cuando te pida la nota SOAP, usa el formato estándar con las 4 secciones claramente separadas. Cuando sugieras diagnósticos, incluye siempre el código CIE-10. Cuando propongas medicamentos, verifica siempre las interacciones con su medicación actual y sus alergias.

Confirma que estás listo.
```

> **Resultado esperado:** Claude confirma que está listo y resume los datos del paciente.

---

## FASE 2: La Consulta Médica

### Paso 2.1 — Motivo de consulta y anamnesis

📋 **PROMPT:**

```
La paciente viene a consulta hoy. Te voy a ir contando lo que me dice y lo que encuentro en la exploración.

CONVERSACIÓN:

Médico: Buenos días María, ¿qué le trae hoy por la consulta?

Paciente: Buenos días doctor. Mire, llevo como dos semanas con dolor en la rodilla derecha. Me duele sobre todo al subir y bajar escaleras y por las mañanas cuando me levanto de la cama noto que está muy rígida, como agarrotada. Tardo como 20 minutos en poder moverla bien.

Médico: ¿Y el dolor cómo es? ¿Le duele todo el día o solo con ciertos movimientos?

Paciente: Es peor con los movimientos. Cuando estoy sentada un rato largo y me levanto también me duele mucho los primeros pasos. Y ayer por la tarde noté que se me había hinchado un poco, la noté caliente.

Médico: ¿Ha tenido fiebre o malestar general?

Paciente: Fiebre no, pero me noto más cansada de lo normal. Y la verdad es que llevo unos meses con un dolor más general en las articulaciones de las manos, sobre todo por las mañanas también.

Médico: ¿Las manos también están rígidas por las mañanas? ¿Cuánto le dura esa rigidez?

Paciente: Sí, sobre todo los nudillos. La rigidez me dura como una hora o así, a veces más.

Con esta información de la anamnesis, ¿qué me llama la atención? ¿Qué sospechas tienes? No me hagas todavía el SOAP completo, primero quiero tu análisis preliminar.
```

> **Resultado esperado:** Claude señala banderas rojas: rigidez matutina >30 min en manos Y rodilla, tumefacción con calor, fatiga. Mencionará al menos artritis reumatoide vs osteoartrosis, y señalará que la rigidez matutina prolongada en manos orienta a proceso inflamatorio.

---

### Paso 2.2 — Exploración física

📋 **PROMPT:**

```
Bien, ahora te cuento lo que encuentro en la exploración física:

EXPLORACIÓN:

Rodilla derecha:
- Inspección: Tumefacción visible en rodilla derecha, leve eritema
- Palpación: Derrame articular moderado, dolor a la presión en interlínea articular medial y lateral, temperatura local aumentada
- Movilidad: Flexión limitada a 100° (normal 135°), extensión completa pero dolorosa en últimos grados
- Test de cajón anterior y posterior: negativos
- Test de McMurray: negativo
- Crepitación palpable durante flexo-extensión

Manos:
- Tumefacción en articulaciones MCF (metacarpofalángicas) 2ª y 3ª de ambas manos
- Tumefacción en articulaciones IFP (interfalángicas proximales) 2ª y 3ª bilateral
- Dolor a la compresión lateral de las MCF bilateralmente (squeeze test positivo)
- No se palpan nódulos de Heberden ni de Bouchard
- Fuerza de prensión disminuida bilateralmente

Constantes:
- TA: 142/88 mmHg
- FC: 78 lpm
- Tª: 36.8°C
- Peso: 82 kg, Talla: 162 cm

Con estos hallazgos de la exploración, actualiza tu análisis. ¿Cuáles son tus dos diagnósticos principales ahora? Dame los códigos CIE-10.
```

> **Resultado esperado:** Claude identifica claramente dos diagnósticos principales:
> 1. **Artritis reumatoide seropositiva/seronegativa** (M05/M06) — por la distribución simétrica en MCF/IFP, rigidez matutina >60min, squeeze test positivo
> 2. **Gonartrosis** (M17) — por la crepitación, limitación de movilidad, pero matiza que el derrame con calor podría ser un brote de AR en rodilla
> Y posiblemente mencione gota poliarticular como diferencial menor.

---

## FASE 3: Nota SOAP Automática

### Paso 3.1 — Generar la nota SOAP completa

📋 **PROMPT:**

```
Perfecto. Ahora genera la nota SOAP completa y estructurada para la historia clínica de esta consulta. Incluye:

- S (Subjetivo): Lo que la paciente refiere
- O (Objetivo): Hallazgos de la exploración
- A (Análisis): Diagnósticos con códigos CIE-10, justificación clínica
- P (Plan): Pruebas solicitadas, tratamiento, seguimiento

Formatea como se pondría en una historia clínica electrónica real.
```

> **Resultado esperado:** Claude genera una nota SOAP completa y profesional con toda la información organizada correctamente, códigos CIE-10, y un plan inicial.

---

## FASE 4: Pruebas Diagnósticas

### Paso 4.1 — Pedir recomendación de pruebas

📋 **PROMPT:**

```
Tenemos dos diagnósticos en la mesa: artritis reumatoide y gonartrosis. ¿Qué pruebas me recomiendas solicitar para confirmar o descartar cada uno? Ordénalas por prioridad y dime qué espero encontrar en cada una si se confirma el diagnóstico.
```

> **Resultado esperado:** Claude recomienda analítica completa (Factor Reumatoide, Anti-CCP, VSG, PCR, hemograma, función renal/hepática, ácido úrico), radiografías de manos AP y rodilla AP+lateral, y posiblemente ecografía articular. Explicará qué resultado esperaría en cada escenario.

### Paso 4.2 — Simular resultados de laboratorio

📋 **PROMPT:**

```
Han llegado los resultados del laboratorio:

- Hemograma: Normal. Hb 12.8 g/dL, Leucocitos 8.200, Plaquetas 310.000
- VSG: 48 mm/h (elevada, normal <20)
- PCR: 3.2 mg/dL (elevada, normal <0.5)
- Factor Reumatoide: 128 UI/mL (positivo alto, normal <14)
- Anti-CCP (anti péptido citrulinado): 245 U/mL (positivo alto, normal <20)
- Glucosa: 142 mg/dL (su DM2)
- HbA1c: 7.4%
- Creatinina: 0.9 mg/dL, FG estimado: 72 mL/min
- Ácido úrico: 5.8 mg/dL (normal)
- GOT/GPT: 28/32 (normal)

Radiografía de rodilla derecha: Pinzamiento del espacio articular medial, osteofitos marginales tibiales, derrame articular visible.

Radiografía de manos: Osteopenia periarticular en MCF y IFP, erosiones incipientes en MCF 2ª y 3ª bilaterales, tumefacción de partes blandas periarticulares.

Con estos resultados, ¿cuál es tu diagnóstico definitivo? Actualiza el análisis.
```

> **Resultado esperado:** Claude confirma Artritis Reumatoide seropositiva (FR+ y Anti-CCP+) con afectación de manos y rodilla. Mencionará los criterios ACR/EULAR 2010 y el score. Mantendrá gonartrosis como comorbilidad.

---

## FASE 5: Prescripción y Posología

### Paso 5.1 — Pedir plan de tratamiento

📋 **PROMPT:**

```
Confirmo el diagnóstico de artritis reumatoide seropositiva con actividad moderada-alta. Necesito que me propongas un plan de tratamiento completo. Ten en cuenta:

1. Es alérgica a AINEs (broncoespasmo)
2. Toma Metformina 850mg/12h y Enalapril 20mg/día
3. Su función renal es FG 72 mL/min
4. Su HbA1c es 7.4% (control subóptimo)

¿Qué medicamentos me recomiendas? Verifica interacciones con su medicación actual.
```

> **Resultado esperado:** Claude propone tratamiento típico de AR: FAME (Metotrexato como primera línea), corticoides a dosis baja como puente (Prednisona), ácido fólico suplementario. Señalará la contraindicación de AINEs y propondrá alternativas para el dolor. Verificará interacciones.

### Paso 5.2 — Pedir posología detallada

📋 **PROMPT:**

```
Dame la posología completa y detallada de cada medicamento que me recomiendas. Para cada uno quiero:

1. Nombre del medicamento (genérico y comercial en España)
2. Dosis exacta
3. Frecuencia de toma
4. Vía de administración
5. Duración del tratamiento
6. Precauciones específicas para esta paciente
7. Qué analíticas de control necesito y cuándo
8. Efectos adversos que debo advertir a la paciente

Formátalo como si fuera para imprimir en una hoja de prescripción.
```

> **Resultado esperado:** Claude genera una prescripción detallada con Metotrexato (dosis, escalado, ácido fólico complementario, controles hepáticos/hematológicos), Prednisona (pauta descendente), analgesia alternativa compatible (Paracetamol o Tramadol si necesario), y protector gástrico. Incluirá monitorización renal por Metformina + Metotrexato.

### Paso 5.3 — Instrucciones para el paciente

📋 **PROMPT:**

```
Ahora necesito que me redactes las instrucciones para la paciente María en lenguaje sencillo, como si se lo fuera a entregar impreso. Que incluya:

1. Qué enfermedad tiene y qué significa (explicación simple)
2. Qué medicamentos nuevos va a tomar y cómo tomarlos
3. Qué síntomas de alarma debe vigilar
4. Cuándo tiene que volver a consulta
5. Qué analíticas tiene que hacerse y cuándo
6. Recomendaciones de estilo de vida (ejercicio, alimentación, etc.)

Usa un tono amable y comprensible, sin jerga médica excesiva.
```

> **Resultado esperado:** Claude genera un documento para el paciente claro, empático y completo.

---

## FASE 6: Análisis de Imagen (Opcional)

### Paso 6.1 — Adjuntar imagen para análisis

> **Nota:** Esta fase requiere adjuntar una imagen en SuperChat. Puedes usar una radiografía de rodilla descargada de internet (busca "knee osteoarthritis X-ray" en Google Imágenes) o cualquier imagen médica que tengas.

📋 **PROMPT (adjuntando la imagen):**

```
Te adjunto la radiografía de rodilla derecha de la paciente María García López (58 años, la que estamos viendo en consulta). Analiza esta imagen y dime:

1. ¿Qué ves en la imagen? Describe los hallazgos radiológicos
2. ¿Hay signos de artrosis? Si sí, ¿qué grado según la clasificación de Kellgren-Lawrence?
3. ¿Ves signos compatibles con artritis inflamatoria (erosiones, osteopenia periarticular)?
4. ¿Es consistente con el cuadro clínico de nuestra paciente?
5. ¿Recomiendas alguna prueba de imagen adicional?

Estructura tu respuesta como un informe radiológico.
```

> **Resultado esperado:** Claude analiza la imagen y genera un informe radiológico estructurado describiendo lo que observa, clasificando el grado de artrosis, y correlacionándolo con el contexto clínico de la paciente.

### Paso 6.2 — Segunda imagen (manos)

> Si tienes una radiografía de manos con erosiones o signos de AR, puedes adjuntarla también.

📋 **PROMPT (adjuntando imagen de manos):**

```
Esta es la radiografía AP de ambas manos de la misma paciente. Analízala buscando específicamente:

1. Osteopenia periarticular
2. Erosiones óseas (especialmente en MCF y IFP)
3. Pinzamiento articular
4. Tumefacción de partes blandas
5. Desviación cubital u otras deformidades

¿Los hallazgos son compatibles con artritis reumatoide? ¿En qué estadio radiológico la clasificarías según Steinbrocker?
```

---

## FASE 7: Preguntas Adicionales de Demostración

Estas son preguntas sueltas que puedes hacer en cualquier momento de la demo para mostrar capacidades adicionales:

### 7.1 — Interacciones medicamentosas

📋 **PROMPT:**

```
La paciente me pregunta si puede tomar Ibuprofeno cuando le duele mucho la rodilla porque dice que es lo que siempre le ha ido bien. ¿Qué le digo? ¿Hay alguna alternativa de venta libre que pueda usar de rescate?
```

### 7.2 — Guías clínicas

📋 **PROMPT:**

```
¿Cuáles son las guías clínicas más actualizadas para el manejo de la artritis reumatoide de debut? Resúmeme las recomendaciones principales de la guía EULAR 2024 para el tratamiento.
```

### 7.3 — Derivación a especialista

📋 **PROMPT:**

```
¿Debo derivar a esta paciente a Reumatología? Si sí, redáctame la hoja de interconsulta con el resumen clínico para el reumatólogo.
```

### 7.4 — Segunda opinión sobre diagnóstico alternativo

📋 **PROMPT:**

```
Un colega me sugiere que podría ser lupus eritematoso sistémico en vez de artritis reumatoide. ¿Es posible? ¿Qué pruebas adicionales necesitaría para diferenciarlo? ¿Cuáles son las diferencias clave entre AR y LES en la presentación de esta paciente?
```

### 7.5 — Comorbilidades

📋 **PROMPT:**

```
Teniendo en cuenta que la paciente es diabética y le voy a poner corticoides (Prednisona), ¿cómo debo ajustar su control glucémico? ¿Necesito modificar la dosis de Metformina? ¿Debería anticiparme con insulina?
```

### 7.6 — Pronóstico

📋 **PROMPT:**

```
La paciente me pregunta: "Doctor, ¿esto se cura? ¿Voy a poder seguir trabajando y haciendo vida normal?" ¿Qué le digo de manera honesta pero esperanzadora?
```

### 7.7 — Evidencia científica reciente

📋 **PROMPT:**

```
¿Hay estudios recientes sobre el uso de inhibidores de JAK (como Tofacitinib o Baricitinib) como alternativa al Metotrexato en artritis reumatoide de debut? ¿Cuáles son los pros y contras respecto al tratamiento clásico?
```

---

## FASE 8: Cierre de la Consulta

### Paso 8.1 — Resumen final

📋 **PROMPT:**

```
Vamos a cerrar la consulta. Genera un resumen completo de todo lo que hemos hecho hoy:

1. Nota SOAP final actualizada con los resultados de laboratorio y radiología
2. Lista de diagnósticos con códigos CIE-10
3. Plan de tratamiento completo con posología
4. Pruebas de control solicitadas con fechas
5. Próxima cita programada
6. Derivaciones realizadas

Formátalo como el registro final de la consulta en la historia clínica electrónica.
```

> **Resultado esperado:** Claude genera un registro de consulta completo y profesional que serviría como entrada en un sistema de historia clínica electrónica real.

---

## Guía Rápida de Demostración

Para una demo rápida de 5 minutos, ejecuta solo estos pasos:

| Paso | Tiempo | Acción |
|------|--------|--------|
| 1 | 0:00 | Paso 1.1 — Configurar rol |
| 2 | 0:30 | Paso 2.1 — Anamnesis |
| 3 | 1:30 | Paso 2.2 — Exploración |
| 4 | 2:30 | Paso 3.1 — Nota SOAP |
| 5 | 3:30 | Paso 5.2 — Posología |
| 6 | 4:30 | Paso 5.3 — Instrucciones paciente |

---

## Notas para el Presentador

### Puntos clave a destacar durante la demo

1. **Velocidad**: Claude genera la nota SOAP en segundos vs los 15-20 minutos que tarda un médico
2. **Seguridad**: Verifica automáticamente alergias e interacciones (el paciente es alérgico a AINEs, Claude nunca los receta)
3. **Códigos CIE-10**: Se generan automáticamente, ahorrando tiempo de codificación
4. **Inteligencia contextual**: Claude recuerda toda la información del paciente durante la consulta
5. **Lenguaje dual**: Genera documentación técnica para el médico E instrucciones simples para el paciente
6. **Análisis de imagen**: Puede interpretar radiografías y correlacionarlas con el cuadro clínico
7. **Evidencia**: Cita guías clínicas y puede buscar evidencia actualizada

### Posibles preguntas del público

| Pregunta | Respuesta sugerida |
|----------|-------------------|
| "¿Sustituye al médico?" | No. Es un asistente que ahorra tiempo en documentación y ofrece soporte a la decisión. El médico siempre decide. |
| "¿Los datos son seguros?" | En producción se usaría un modelo on-premise o con acuerdo HIPAA/RGPD. Esta demo es con datos ficticios. |
| "¿Funciona en tiempo real?" | La visión es que transcriba la conversación en tiempo real (Whisper) y genere todo automáticamente. Esta demo muestra el flujo paso a paso. |
| "¿Qué precisión tiene en el diagnóstico?" | El diagnóstico siempre es del médico. La IA sugiere basándose en la evidencia y el contexto, pero no diagnostica por sí sola. |

---

## Escenario Alternativo: Paciente Pediátrico

Si quieres variar la demo, puedes usar este escenario alternativo:

📋 **PROMPT para segundo escenario:**

```
Nuevo paciente. Configura estos datos:

- Pablo Martínez Ruiz, 8 años, varón
- Peso: 28 kg, Talla: 130 cm
- Sin antecedentes de interés, vacunación al día
- Sin alergias conocidas
- Sin medicación habitual

Motivo de consulta: Su madre le trae porque lleva 3 días con fiebre de 38.5-39°C, dolor de garganta intenso, y desde ayer tiene un sarpullido rojizo en el tronco y pliegues. No ha comido bien. Esta mañana le ha visto la lengua blanca con puntitos rojos.

¿Qué sospechas? Hazme el diagnóstico diferencial y proponme el plan.
```

> **Resultado esperado:** Claude identifica escarlatina (A38) como diagnóstico principal, con faringoamigdalitis estreptocócica (J02.0) como alternativa, solicita test rápido de estreptococo, y prescribe Amoxicilina (ajustada a peso pediátrico) con posología precisa.

---

*Documento creado: Febrero 2026*
*Proyecto: SoulInTheBot / Medicum Demo*
*Uso: Demostración de capacidades de IA clínica con Claude vía SuperChat*
