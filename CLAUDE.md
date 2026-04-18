# Instrucciones para Claude Code

## Ramas protegidas

- **NUNCA** hacer `git push` directo a `main` o `develop`. Siempre crear una rama y un Pull Request.
- Si el remote advierte "Changes must be made through a pull request", **detenerse** y preguntar al usuario antes de continuar.

## Commits

Todos los mensajes de commit deben seguir la especificación **Conventional Commits** (https://www.conventionalcommits.org/).

### Formato

```
<tipo>(alcance opcional): descripción breve en español

Cuerpo opcional con más detalle.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

### Tipos permitidos

| Tipo       | Cuándo usarlo                                      |
|------------|-----------------------------------------------------|
| `feat`     | Nueva funcionalidad o notebook                      |
| `fix`      | Corrección de errores                               |
| `docs`     | Cambios en documentación (README, CLAUDE.md, etc.)  |
| `style`    | Formato, espacios, comas — sin cambios de lógica    |
| `refactor` | Reestructuración de código sin cambiar comportamiento |
| `test`     | Agregar o modificar tests                           |
| `chore`    | Tareas de mantenimiento (dependencias, configs)     |
| `data`     | Cambios en datasets o archivos de datos             |

### Reglas

- La descripción debe estar en **español** y en **minúsculas** (sin punto final).
- Máximo **72 caracteres** en la primera línea.
- Si el commit incluye un cambio importante o breaking change, agregar `BREAKING CHANGE:` en el cuerpo o `!` después del tipo (e.g. `feat!: ...`).
- Un commit debe abarcar **un solo cambio lógico**. No mezclar cambios no relacionados.

### Ejemplos

```
feat: agregar modelo de regresión lineal para predicción de ventas
```

```
docs: actualizar README con instrucciones de instalación
```

```
chore: agregar dependencias de scikit-learn en requirements.txt
```

```
fix(notebook): corregir error en la celda de evaluación del modelo
```
