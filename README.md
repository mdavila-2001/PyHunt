# 🦆 PyHunt - Duck Hunt con IA Avanzada

Un juego moderno de Duck Hunt desarrollado en Python con inteligencia artificial adaptativa, reconocimiento de gestos y múltiples modos de juego.

## 🎮 Características Principales

### 🤖 **IA Adaptativa Avanzada**
- **Patos Inteligentes**: Los patos aprenden de tu comportamiento y se vuelven más difíciles
- **Estados de Comportamiento**: Normal, Evasivo, Agresivo, Patrulla, Caza y Retirada
- **Memoria AI**: Los patos recuerdan posiciones peligrosas y estrategias exitosas
- **Personalidad**: Cada pato tiene rasgos únicos (coraje, inteligencia, agilidad)
- **Predicción**: Los patos predicen tus movimientos basándose en patrones

### 🎯 **Múltiples Modos de Juego**
- **Clásico**: El modo original de Duck Hunt
- **Supervivencia**: Los patos se vuelven más rápidos y agresivos con el tiempo
- **Contra Reloj**: Dispara tantos patos como puedas en 30 segundos
- **Precisión**: Solo tienes 10 disparos, ¡cada tiro debe contar!
- **Jefe Final**: Enfréntate a patos gigantes que requieren múltiples disparos
- **Infinito**: Juego sin fin con IA adaptativa
- **Desafío**: Modo aleatorio con reglas cambiantes

### ⚡ **Sistema de Power-ups**
- **Disparo Rápido**: Aumenta la velocidad de disparo
- **Puntos Dobles**: Duplica los puntos obtenidos
- **Cámara Lenta**: Ralentiza el tiempo para mejor precisión
- **Disparo Múltiple**: Dispara varios proyectiles a la vez
- **Escudo**: Protección temporal contra penalizaciones
- **Imán**: Atrae power-ups hacia ti
- **Congelación**: Congela temporalmente a los patos

### 🏆 **Sistema de Logros**
- **15+ Logros**: Desbloquea logros por precisión, puntuación y habilidad
- **Puntos de Logros**: Gana puntos por completar logros
- **Progresión**: Sistema de niveles basado en logros desbloqueados
- **Logros Especiales**: Logros únicos para cada modo de juego

### 📊 **Estadísticas y Leaderboards**
- **Estadísticas Detalladas**: Seguimiento completo del rendimiento
- **Leaderboards**: Tablas de clasificación por modo y general
- **Tendencias**: Análisis de mejora a lo largo del tiempo
- **Exportación**: Exporta tus estadísticas para análisis

### 👋 **Reconocimiento de Gestos**
- **Control por Manos**: Usa gestos para controlar el juego
- **Múltiples Gestos**: Mano abierta, cerrada, dedo índice, paz, pulgar
- **Detección en Tiempo Real**: Reconocimiento instantáneo de gestos
- **Configuración**: Ajusta la sensibilidad y mapeo de gestos

## 🚀 Instalación

### Requisitos
- Python 3.8 o superior
- Cámara web (para reconocimiento de gestos)

### Instalación Rápida
```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/pyhunt.git
cd pyhunt

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el juego
python ai_duck_hunt.py
```

### Dependencias Principales
```
pygame>=2.0.0
opencv-python>=4.5.0
mediapipe>=0.10.0
numpy>=1.21.0
```

## 🎮 Controles

### Controles Básicos
- **Mouse**: Mover cursor y disparar
- **P**: Pausar/Reanudar
- **ESC**: Salir
- **ENTER**: Iniciar juego
- **R**: Reiniciar (en fin de juego)

### Controles por Gestos
- **Mano Abierta**: Mover cursor
- **Mano Cerrada**: Disparar
- **Dedo Índice**: Apuntar
- **Paz**: Volver al menú
- **Pulgar**: Pausar

## 🎯 Modos de Juego

### Clásico
El modo original de Duck Hunt. Dispara patos en 60 segundos.
- **Duración**: 60 segundos
- **IA**: Nivel 1
- **Objetivo**: Máxima puntuación

### Supervivencia
Los patos se vuelven más rápidos y agresivos con el tiempo.
- **Duración**: Infinita
- **IA**: Aumenta cada 30 segundos
- **Objetivo**: Sobrevivir el mayor tiempo posible

### Contra Reloj
Dispara tantos patos como puedas en 30 segundos.
- **Duración**: 30 segundos
- **Spawn**: Rápido (1 segundo)
- **Objetivo**: Máxima cantidad de patos

### Precisión
Solo tienes 10 disparos. ¡Cada tiro debe contar!
- **Disparos**: Limitados a 10
- **Puntos**: Dobles por precisión
- **Objetivo**: Máxima precisión

### Jefe Final
Enfréntate a patos gigantes y poderosos.
- **Duración**: 2 minutos
- **Patos**: Gigantes con múltiples vidas
- **Objetivo**: Derrotar jefes

### Infinito
Juego sin fin con IA adaptativa.
- **Duración**: Sin límite
- **IA**: Adaptativa
- **Objetivo**: Progresión continua

### Desafío
Modo aleatorio con reglas cambiantes.
- **Duración**: 90 segundos
- **Reglas**: Cambian cada 15 segundos
- **Objetivo**: Adaptarse a cambios

## 🤖 Sistema de IA

### Estados de Comportamiento
1. **Normal**: Vuelo básico con movimiento aleatorio
2. **Evasivo**: Evita al jugador activamente
3. **Agresivo**: Se acerca al jugador
4. **Patrulla**: Sigue rutas sistemáticas
5. **Caza**: Busca y predice movimientos del jugador
6. **Retirada**: Huye hacia los bordes de la pantalla

### Memoria AI
- **Posiciones del Jugador**: Historial de movimientos
- **Evaciones Exitosas**: Técnicas que funcionaron
- **Áreas Peligrosas**: Zonas donde fueron golpeados
- **Precisión del Jugador**: Adaptación a la habilidad

### Rasgos de Personalidad
- **Coraje**: Determina agresividad (0.3 - 0.8)
- **Inteligencia**: Capacidad de aprendizaje (0.5 - 1.0)
- **Agilidad**: Habilidad de evasión (0.6 - 1.0)

## ⚡ Power-ups

### Tipos Disponibles
- **⚡ Disparo Rápido**: 3x velocidad de disparo (10s)
- **💰 Puntos Dobles**: 2x puntos (15s)
- **⏰ Cámara Lenta**: 0.5x velocidad de tiempo (8s)
- **🎯 Disparo Múltiple**: Múltiples proyectiles (12s)
- **🛡️ Escudo**: Protección (10s)
- **🧲 Imán**: Atrae power-ups (12s)
- **❄️ Congelación**: Congela patos (6s)

### Mecánicas
- **Spawn**: Cada 15 segundos con 30% de probabilidad
- **Duración**: Efectos temporales con indicadores visuales
- **Stacking**: Los efectos se pueden combinar
- **Cooldown**: Prevención de spam

## 🏆 Logros

### Categorías
- **🎯 Precisión**: Logros por precisión de disparo
- **💰 Puntuación**: Logros por puntuación alta
- **🦆 Patos**: Logros por cantidad de patos abatidos
- **🤖 IA**: Logros por enfrentar IA avanzada
- **🎮 Dedicatoria**: Logros por tiempo jugado
- **⚡ Especiales**: Logros únicos y desafiantes

### Ejemplos de Logros
- **Sharp Shooter**: 90% precisión en una partida
- **Duck Legend**: 5000 puntos en una partida
- **AI Master**: Alcanzar nivel 10 de IA
- **Speed Demon**: 5 patos en 30 segundos
- **Perfect Shot**: 100% precisión

## 📊 Estadísticas

### Métricas Rastreadas
- **Partidas Totales**: Número de juegos completados
- **Puntuación Total**: Suma de todas las puntuaciones
- **Precisión Promedio**: Precisión general
- **Mejor Puntuación**: Puntuación más alta
- **Tiempo de Juego**: Tiempo total jugado
- **Racha Actual**: Partidas consecutivas exitosas
- **Logros Desbloqueados**: Progreso de logros

### Leaderboards
- **General**: Clasificación global
- **Por Modo**: Clasificaciones específicas por modo
- **Diario**: Mejores puntuaciones del día
- **Semanal**: Mejores puntuaciones de la semana

## 🎨 Características Técnicas

### Arquitectura Modular
- **Asset Manager**: Gestión de recursos
- **Game Engine**: Motor principal del juego
- **UI Manager**: Interfaz de usuario
- **Input Manager**: Gestión de entrada
- **Gesture Controller**: Control por gestos
- **Achievement System**: Sistema de logros
- **Power-up System**: Sistema de power-ups
- **Statistics System**: Estadísticas y leaderboards

### Optimizaciones
- **FPS**: 60 FPS constante
- **Memoria**: Gestión eficiente de sprites
- **Rendimiento**: Optimización para diferentes hardware
- **Escalabilidad**: Fácil adición de nuevas características

## 🔧 Configuración

### Archivos de Configuración
- `config.py`: Configuración general del juego
- `ai_data.json`: Datos de aprendizaje de IA
- `achievements.json`: Progreso de logros
- `player_stats.json`: Estadísticas del jugador
- `leaderboards.json`: Tablas de clasificación

### Personalización
- **Dificultad**: Ajuste de niveles de IA
- **Sensibilidad**: Configuración de gestos
- **Sonido**: Volumen y efectos
- **Visuales**: Efectos y animaciones

## 🐛 Solución de Problemas

### Problemas Comunes
1. **Cámara no detectada**: Verificar conexión y permisos
2. **Bajo FPS**: Reducir configuración gráfica
3. **Gestos no funcionan**: Ajustar iluminación
4. **Sonido no funciona**: Verificar drivers de audio

### Logs y Debug
- Los logs se guardan en archivos JSON
- Modo debug disponible con información de IA
- Exportación de datos para análisis

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

### Áreas de Mejora
- Nuevos modos de juego
- Efectos visuales avanzados
- IA más sofisticada
- Nuevos power-ups
- Modo multijugador
- Soporte para móviles

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🙏 Agradecimientos

- **Pygame**: Motor de juegos
- **OpenCV**: Visión por computadora
- **MediaPipe**: Detección de gestos
- **Comunidad**: Feedback y sugerencias

---

**¡Disfruta cazando patos con IA avanzada! 🦆🎯**
