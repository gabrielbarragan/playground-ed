# Soporte para Código micro:bit Python en el Sandbox

## Problema

Cuando los estudiantes escriben código que usa la librería `microbit` (ej. `from microbit import *`), el sandbox falla con `ModuleNotFoundError` porque el módulo no existe en el entorno de ejecución.

## Objetivo

Proveer un módulo stub `microbit` dentro del sandbox para que el código de los estudiantes **no falle al importar**, y las funciones principales de la API micro:bit sean no-ops silenciosos o devuelvan valores simulados razonables.

No se busca emular hardware real — solo que el código sea ejecutable sin errores para que pueda ser evaluado o probado en la plataforma.

## Estado Actual

- El sandbox ya soporta módulos stub via la carpeta `app/sandbox_modules/` (`process.py:24-26`).
- `PYTHONPATH` apunta a esa carpeta en el entorno limpio del subprocess (`process.py:36`).
- Ya existe un precedente: `app/sandbox_modules/turtle.py` implementa un stub de turtle que emite comandos gráficos via `__GFX__`.
- Cualquier módulo/paquete que se agregue ahí estará disponible automáticamente en el sandbox sin cambios en `process.py`.

## Cambios Propuestos

### Crear paquete `app/sandbox_modules/microbit/`

Estructura:

```
app/sandbox_modules/microbit/
├── __init__.py      # re-exporta todo (from microbit import * funciona)
├── display.py       # clase Image y objeto display (show, scroll, clear)
├── io.py            # clases pin0..pin20, button_a, button_b, accelerometer, compass
└── music.py         # módulo music (play, pitch, stop, etc.)
```

### API a implementar (stubs no-op)

**`__init__.py`** — Exporta todos los objetos que `from microbit import *` espera:
- `display` — objeto con métodos `show()`, `scroll()`, `clear()`, `set_pixel()`, `get_pixel()`.
- `Image` — clase con constantes predefinidas (`Image.HEART`, `Image.HAPPY`, etc.) y constructor que acepta strings.
- `button_a`, `button_b` — objetos con `is_pressed()` → `False`, `was_pressed()` → `False`, `get_presses()` → `0`.
- `pin0` a `pin20` — objetos con `read_digital()` → `0`, `write_digital()`, `read_analog()` → `0`, `write_analog()`, `is_touched()` → `False`.
- `accelerometer` — objeto con `get_x/y/z()` → `0`, `get_values()` → `(0,0,0)`, `get_strength()` → `0`.
- `compass` — objeto con `heading()` → `0`, `calibrate()`, `is_calibrated()` → `True`.
- `sleep(ms)` — llama a `time.sleep(ms/1000)` (real, acotado por el timeout del sandbox).
- `running_time()` — retorna milisegundos desde el import.
- `temperature()` → `21` (valor fijo razonable).
- `panic(code)` — print y `sys.exit(1)`.
- `reset()` — no-op.

**`music.py`** — Stub para `import music`:
- `play()`, `pitch()`, `stop()`, `reset()` — no-ops.
- Constantes de notas: `DADADADUM`, `ENTERTAINER`, etc. como strings vacíos.

### Qué NO se implementa

- **Emulación visual** del display 5x5 (no se envían eventos `__GFX__` por ahora).
- **Interacción con hardware real** — todo es simulado con valores por defecto.
- **Módulos secundarios**: `radio`, `i2c`, `spi`, `uart`, `neopixel` — se pueden agregar después como stubs vacíos si los estudiantes los necesitan.

## Archivos a Crear/Modificar

| Archivo | Acción |
|---|---|
| `app/sandbox_modules/microbit/__init__.py` | Crear — exporta display, Image, buttons, pins, accelerometer, compass, sleep, etc. |
| `app/sandbox_modules/microbit/display.py` | Crear — clase Image y objeto display |
| `app/sandbox_modules/microbit/io.py` | Crear — pins, buttons, accelerometer, compass |
| `app/sandbox_modules/microbit/music.py` | Crear — stubs de funciones de música |

No se necesitan cambios en el backend ni en el frontend — el mecanismo de `PYTHONPATH` ya resuelve la disponibilidad del módulo.

## Tasks

- [ ] **SB-1**: Crear directorio `app/sandbox_modules/microbit/`
- [ ] **SB-2**: Implementar `display.py` — clase `Image` con constantes predefinidas (`HEART`, `HAPPY`, `SAD`, `SMILE`, `YES`, `NO`, etc.) y constructor que acepta strings; objeto `display` con métodos `show()`, `scroll()`, `clear()`, `set_pixel()`, `get_pixel()`
- [ ] **SB-3**: Implementar `io.py` — clase `Button` (`is_pressed()` → `False`, `was_pressed()` → `False`, `get_presses()` → `0`); clase `Pin` (`read_digital()` → `0`, `write_digital()`, `read_analog()` → `0`, `write_analog()`, `is_touched()` → `False`); clase `Accelerometer` (`get_x/y/z()` → `0`, `get_values()` → `(0,0,0)`, `get_strength()` → `0`); clase `Compass` (`heading()` → `0`, `calibrate()`, `is_calibrated()` → `True`); instanciar `button_a`, `button_b`, `pin0`–`pin20`, `accelerometer`, `compass`
- [ ] **SB-4**: Implementar `music.py` — funciones `play()`, `pitch()`, `stop()`, `reset()` como no-ops; constantes de melodías (`DADADADUM`, `ENTERTAINER`, `PRELUDE`, `ODE`, `NYAN`, `RINGTONE`, etc.) como strings vacíos
- [ ] **SB-5**: Implementar `__init__.py` — re-exportar todo desde `display`, `io`, `music`; implementar `sleep(ms)` con `time.sleep(ms/1000)`, `running_time()` con timestamp desde import, `temperature()` → `21`, `panic()` con `sys.exit(1)`, `reset()` no-op
- [ ] **SB-6**: Verificar que `from microbit import *` no lanza error en el sandbox
- [ ] **SB-7**: Verificar que `display.show(Image.HEART)` ejecuta sin error
- [ ] **SB-8**: Verificar que `button_a.is_pressed()` retorna `False` y no genera loop infinito
- [ ] **SB-9**: Verificar que `sleep(1000)` pausa 1s real (acotado por timeout de 10s del sandbox)
- [ ] **SB-10**: Probar código típico micro:bit escolar de extremo a extremo (import, display, buttons, sleep)

## Requerimientos (Gherkin)

```gherkin
Feature: Soporte para código micro:bit Python en el sandbox
  Como estudiante
  Quiero ejecutar código que usa la librería microbit en el playground
  Para poder practicar y probar mis programas de micro:bit sin errores de importación

  # ── Importación ───────────────────────────────────────────────

  Scenario: Importar microbit con wildcard
    Given el estudiante escribe código con "from microbit import *"
    When ejecuta el código en el sandbox
    Then la ejecución finaliza sin ModuleNotFoundError
    And el return_code es 0

  Scenario: Importar microbit con import directo
    Given el estudiante escribe código con "import microbit"
    When ejecuta el código en el sandbox
    Then la ejecución finaliza sin ModuleNotFoundError
    And el return_code es 0

  Scenario: Importar módulo music
    Given el estudiante escribe código con "import music"
    When ejecuta el código en el sandbox
    Then la ejecución finaliza sin ModuleNotFoundError
    And el return_code es 0

  # ── Display e Image ───────────────────────────────────────────

  Scenario: Usar display.show con Image predefinida
    Given el estudiante escribe código:
      """
      from microbit import *
      display.show(Image.HEART)
      """
    When ejecuta el código en el sandbox
    Then la ejecución finaliza sin error
    And el return_code es 0

  Scenario: Usar display.scroll con texto
    Given el estudiante escribe código:
      """
      from microbit import *
      display.scroll("Hola")
      """
    When ejecuta el código en el sandbox
    Then la ejecución finaliza sin error

  Scenario: Usar display.set_pixel y get_pixel
    Given el estudiante escribe código:
      """
      from microbit import *
      display.set_pixel(2, 2, 9)
      valor = display.get_pixel(2, 2)
      """
    When ejecuta el código en el sandbox
    Then la ejecución finaliza sin error

  Scenario: Usar display.clear
    Given el estudiante escribe código:
      """
      from microbit import *
      display.clear()
      """
    When ejecuta el código en el sandbox
    Then la ejecución finaliza sin error

  Scenario: Crear Image personalizada
    Given el estudiante escribe código:
      """
      from microbit import *
      mi_imagen = Image("09090:90909:90009:09090:00900")
      display.show(mi_imagen)
      """
    When ejecuta el código en el sandbox
    Then la ejecución finaliza sin error

  # ── Botones ───────────────────────────────────────────────────

  Scenario: Consultar estado de botones sin loop infinito
    Given el estudiante escribe código:
      """
      from microbit import *
      if button_a.is_pressed():
          display.show(Image.HAPPY)
      """
    When ejecuta el código en el sandbox
    Then la ejecución finaliza sin error
    And button_a.is_pressed() retorna False por defecto
    And el código no entra en loop infinito

  Scenario: Usar was_pressed y get_presses
    Given el estudiante escribe código:
      """
      from microbit import *
      a = button_a.was_pressed()
      b = button_b.get_presses()
      """
    When ejecuta el código en el sandbox
    Then la ejecución finaliza sin error

  # ── Pines ─────────────────────────────────────────────────────

  Scenario: Leer y escribir pines digitales
    Given el estudiante escribe código:
      """
      from microbit import *
      pin0.write_digital(1)
      valor = pin0.read_digital()
      """
    When ejecuta el código en el sandbox
    Then la ejecución finaliza sin error

  Scenario: Leer y escribir pines analógicos
    Given el estudiante escribe código:
      """
      from microbit import *
      pin1.write_analog(512)
      valor = pin1.read_analog()
      """
    When ejecuta el código en el sandbox
    Then la ejecución finaliza sin error

  # ── Sensores ──────────────────────────────────────────────────

  Scenario: Leer acelerómetro
    Given el estudiante escribe código:
      """
      from microbit import *
      x = accelerometer.get_x()
      valores = accelerometer.get_values()
      """
    When ejecuta el código en el sandbox
    Then la ejecución finaliza sin error
    And get_x() retorna 0
    And get_values() retorna (0, 0, 0)

  Scenario: Leer brújula
    Given el estudiante escribe código:
      """
      from microbit import *
      angulo = compass.heading()
      calibrado = compass.is_calibrated()
      """
    When ejecuta el código en el sandbox
    Then la ejecución finaliza sin error
    And heading() retorna 0
    And is_calibrated() retorna True

  Scenario: Leer temperatura
    Given el estudiante escribe código:
      """
      from microbit import *
      temp = temperature()
      print(temp)
      """
    When ejecuta el código en el sandbox
    Then la salida stdout contiene "21"

  # ── Funciones de tiempo ───────────────────────────────────────

  Scenario: sleep pausa la ejecución real
    Given el estudiante escribe código:
      """
      from microbit import *
      sleep(500)
      print("listo")
      """
    When ejecuta el código en el sandbox
    Then la ejecución tarda aproximadamente 500ms
    And la salida stdout contiene "listo"

  Scenario: sleep largo es acotado por timeout del sandbox
    Given el estudiante escribe código:
      """
      from microbit import *
      sleep(30000)
      """
    When ejecuta el código en el sandbox
    Then la ejecución es terminada por el timeout de 10s del sandbox

  Scenario: running_time retorna milisegundos
    Given el estudiante escribe código:
      """
      from microbit import *
      t = running_time()
      print(type(t).__name__)
      """
    When ejecuta el código en el sandbox
    Then la salida stdout contiene "int"

  # ── Música ────────────────────────────────────────────────────

  Scenario: Reproducir melodía predefinida
    Given el estudiante escribe código:
      """
      import music
      music.play(music.DADADADUM)
      """
    When ejecuta el código en el sandbox
    Then la ejecución finaliza sin error

  Scenario: Usar pitch y stop
    Given el estudiante escribe código:
      """
      import music
      music.pitch(440, 500)
      music.stop()
      """
    When ejecuta el código en el sandbox
    Then la ejecución finaliza sin error

  # ── Programa completo típico ──────────────────────────────────

  Scenario: Programa escolar completo ejecuta sin errores
    Given el estudiante escribe código:
      """
      from microbit import *
      import music

      display.scroll("Hola")
      sleep(500)

      if button_a.is_pressed():
          display.show(Image.HAPPY)
          music.play(music.DADADADUM)
      else:
          display.show(Image.SAD)

      temp = temperature()
      print("Temperatura:", temp)
      display.clear()
      """
    When ejecuta el código en el sandbox
    Then la ejecución finaliza sin error
    And la salida stdout contiene "Temperatura: 21"
```
