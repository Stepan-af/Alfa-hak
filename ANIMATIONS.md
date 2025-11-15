# 🎨 Руководство по анимациям Alfa Copilot

## Стандарты анимаций

Все анимации соответствуют требованиям ТЗ и бренд-стилю Alfa-Bank:

- **Enter анимации:** 280-360ms с easeOutCubic (`cubic-bezier(0.215, 0.610, 0.355, 1.000)`)
- **Exit анимации:** 220-260ms с easeInCubic (`cubic-bezier(0.550, 0.055, 0.675, 0.190)`)
- **Hover эффекты:** scale 1.02, подъем на 2-4px
- **Accessibility:** Автоматически отключаются при `prefers-reduced-motion`

## Использование Composables

### 1. Анимация появления карточки

```vue
<script setup>
import { ref } from 'vue'
import { useCardEnterAnimation } from '@/composables/useAnimations'

const cardRef = ref(null)
useCardEnterAnimation(cardRef, 0.2) // delay 200ms
</script>

<template>
  <div ref="cardRef" class="card">
    Content
  </div>
</template>
```

### 2. Анимация списка с задержкой (stagger)

```vue
<script setup>
import { ref } from 'vue'
import { useListEnterAnimation } from '@/composables/useAnimations'

const listRef = ref(null)
useListEnterAnimation(listRef, '.list-item', 0.08)
</script>

<template>
  <div ref="listRef">
    <div class="list-item">Item 1</div>
    <div class="list-item">Item 2</div>
    <div class="list-item">Item 3</div>
  </div>
</template>
```

### 3. Hover эффект

```vue
<script setup>
import { ref } from 'vue'
import { useHoverEffect } from '@/composables/useAnimations'

const buttonRef = ref(null)
const { isHovered } = useHoverEffect(buttonRef)
</script>

<template>
  <button ref="buttonRef">
    Hover me
  </button>
</template>
```

### 4. Анимированный счетчик

```vue
<script setup>
import { ref, watch } from 'vue'
import { useCounterAnimation } from '@/composables/useAnimations'

const targetValue = ref(1000)
const { displayValue, animate } = useCounterAnimation(targetValue)

// Запуск анимации
watch(targetValue, (newValue) => {
  animate(newValue)
})
</script>

<template>
  <div>{{ displayValue }}</div>
</template>
```

### 5. Анимация модального окна

```vue
<script setup>
import { ref } from 'vue'
import { useModalAnimation } from '@/composables/useAnimations'

const isOpen = ref(false)
const overlayRef = ref(null)
const contentRef = ref(null)

const { animateIn, animateOut } = useModalAnimation(isOpen, overlayRef, contentRef)

const openModal = () => {
  isOpen.value = true
  animateIn()
}

const closeModal = () => {
  animateOut()
  setTimeout(() => {
    isOpen.value = false
  }, 240) // exit duration
}
</script>
```

## Использование CSS классов

### Готовые анимации

```html
<!-- Fade animations -->
<div class="fade-in">Появляется с затуханием</div>
<div class="fade-in-up">Появляется снизу</div>
<div class="fade-in-down">Появляется сверху</div>

<!-- Scale animations -->
<div class="scale-in">Увеличивается</div>

<!-- Special effects -->
<div class="bounce">Прыгает</div>
<div class="pulse">Пульсирует</div>
<div class="shake">Трясется</div>
```

### Hover эффекты

```html
<div class="hover-lift">
  Поднимается при наведении
</div>

<div class="hover-scale">
  Увеличивается при наведении
</div>

<div class="hover-glow">
  Светится при наведении
</div>
```

### Задержки (stagger)

```html
<div class="fade-in-up stagger-1">Item 1</div>
<div class="fade-in-up stagger-2">Item 2</div>
<div class="fade-in-up stagger-3">Item 3</div>
```

### Скелетон для загрузки

```html
<div class="skeleton" style="width: 200px; height: 20px;"></div>
```

## Готовые компоненты

### StatCard - Карточка статистики

```vue
<StatCard
  :value="12500"
  label="Чистая прибыль"
  icon="mdi-cash"
  color="success"
  trend="+12.5%"
  trend-direction="up"
  :delay="0.1"
  animated
/>
```

**Props:**
- `value` - Числовое значение (анимируется)
- `label` - Название метрики
- `icon` - MDI иконка
- `color` - Цвет темы: `primary | success | warning | error | info`
- `trend` - Тренд (например "+12.5%")
- `trendDirection` - Направление: `up | down | neutral`
- `delay` - Задержка анимации в секундах
- `animated` - Включить анимации

### ActionButton - Кнопка с анимацией

```vue
<ActionButton
  label="Создать"
  icon="mdi-plus"
  color="primary"
  size="large"
  animated
  @click="handleClick"
/>
```

### ChatMessage - Сообщение чата

```vue
<ChatMessage
  :message="messageData"
  :is-typing="false"
  :delay="0.1"
  animated
  @feedback="handleFeedback"
/>
```

## Константы анимаций

Используйте константы из composable для единообразия:

```typescript
import { ALFA_ANIMATION } from '@/composables/useAnimations'

// Длительности
ALFA_ANIMATION.duration.enter // 0.36s
ALFA_ANIMATION.duration.exit  // 0.24s
ALFA_ANIMATION.duration.quick // 0.28s
ALFA_ANIMATION.duration.slow  // 0.5s

// Easing
ALFA_ANIMATION.ease.enter  // 'power3.out'
ALFA_ANIMATION.ease.exit   // 'power3.in'
ALFA_ANIMATION.ease.smooth // 'power2.inOut'

// Hover
ALFA_ANIMATION.hover.scale    // 1.02
ALFA_ANIMATION.hover.y        // -4
ALFA_ANIMATION.hover.duration // 0.2
```

## Accessibility

Все анимации автоматически отключаются для пользователей с `prefers-reduced-motion: reduce`. Не требуется дополнительная настройка.

## Best Practices

1. **Используйте анимации осмысленно** - не перегружайте интерфейс
2. **Применяйте stagger для списков** - создает эффект "волны"
3. **Добавляйте delay для последовательности** - важные элементы анимируются первыми
4. **Hover эффекты для интерактивных элементов** - кнопки, карточки, ссылки
5. **Используйте константы** - для единообразия анимаций

## Примеры в проекте

- **HomeView.vue** - Анимация статистических карточек с stagger
- **ActionButton.vue** - Hover эффект для кнопок
- **StatCard.vue** - Анимированные счетчики
- **ChatMessage.vue** - Появление сообщений, typing indicator

## Производительность

- Все анимации используют `transform` и `opacity` для оптимизации
- Добавлен `will-change` для элементов с hover эффектами
- GPU-ускорение через `translate3d` и `perspective`
- Animations отключаются при `prefers-reduced-motion`
