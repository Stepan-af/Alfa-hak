import { ref, onMounted, onBeforeUnmount, type Ref } from 'vue'
import { gsap } from 'gsap'

/**
 * Получить DOM элемент из ref (работает с Vue компонентами)
 */
const getElement = (elementRef: Ref<any>): HTMLElement | null => {
  if (!elementRef.value) return null
  
  // Если это Vue компонент, получаем $el
  if (elementRef.value.$el) {
    return elementRef.value.$el
  }
  
  // Если это уже DOM элемент
  if (elementRef.value instanceof HTMLElement) {
    return elementRef.value
  }
  
  return null
}

/**
 * Composable для анимаций в стиле Alfa-Bank
 * - Enter: 280-360ms с easeOutCubic
 * - Exit: 220-260ms с easeInCubic
 * - Hover: scale 1.02, подъем на 2-4px
 * - Учитывает prefers-reduced-motion
 */

// Проверка на предпочтение пользователя уменьшить анимации
const prefersReducedMotion = () => {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

// Стандартные настройки анимаций Alfa
export const ALFA_ANIMATION = {
  duration: {
    enter: 0.36, // 360ms
    exit: 0.24,  // 240ms
    quick: 0.28, // 280ms
    slow: 0.5    // 500ms
  },
  ease: {
    enter: 'power3.out',  // easeOutCubic
    exit: 'power3.in',    // easeInCubic
    smooth: 'power2.inOut'
  },
  hover: {
    scale: 1.02,
    y: -4,
    duration: 0.2
  }
}

/**
 * Анимация появления карточки (fade + slide up)
 */
export function useCardEnterAnimation(elementRef: Ref<any>, delay = 0) {
  onMounted(() => {
    const element = getElement(elementRef)
    if (!element || prefersReducedMotion()) return

    gsap.from(element, {
      y: 24,
      opacity: 0,
      duration: ALFA_ANIMATION.duration.enter,
      ease: ALFA_ANIMATION.ease.enter,
      delay
    })
  })
}

/**
 * Анимация появления списка элементов (stagger)
 */
export function useListEnterAnimation(
  containerRef: Ref<any>,
  itemSelector = '.list-item',
  staggerDelay = 0.08
) {
  onMounted(() => {
    const container = getElement(containerRef)
    if (!container || prefersReducedMotion()) return

    const items = container.querySelectorAll(itemSelector)
    
    gsap.from(items, {
      y: 16,
      opacity: 0,
      duration: ALFA_ANIMATION.duration.quick,
      ease: ALFA_ANIMATION.ease.enter,
      stagger: staggerDelay
    })
  })
}

/**
 * Hover эффект для карточек/кнопок
 */
export function useHoverEffect(elementRef: Ref<any>) {
  const isHovered = ref(false)

  const handleMouseEnter = () => {
    if (prefersReducedMotion()) return
    
    isHovered.value = true
    const element = getElement(elementRef)
    if (!element) return
    
    gsap.to(element, {
      y: ALFA_ANIMATION.hover.y,
      scale: ALFA_ANIMATION.hover.scale,
      duration: ALFA_ANIMATION.hover.duration,
      ease: ALFA_ANIMATION.ease.smooth
    })
  }

  const handleMouseLeave = () => {
    if (prefersReducedMotion()) return
    
    isHovered.value = false
    const element = getElement(elementRef)
    if (!element) return
    
    gsap.to(element, {
      y: 0,
      scale: 1,
      duration: ALFA_ANIMATION.hover.duration,
      ease: ALFA_ANIMATION.ease.smooth
    })
  }

  onMounted(() => {
    const element = getElement(elementRef)
    if (!element) return
    
    element.addEventListener('mouseenter', handleMouseEnter)
    element.addEventListener('mouseleave', handleMouseLeave)
  })

  onBeforeUnmount(() => {
    const element = getElement(elementRef)
    if (!element) return
    
    element.removeEventListener('mouseenter', handleMouseEnter)
    element.removeEventListener('mouseleave', handleMouseLeave)
  })

  return { isHovered }
}

/**
 * Анимация счетчиков (counter animation)
 */
export function useCounterAnimation(
  duration = 1.5
) {
  const displayValue = ref(0)

  const animate = (newValue: number) => {
    if (prefersReducedMotion()) {
      displayValue.value = newValue
      return
    }

    gsap.to(displayValue, {
      value: newValue,
      duration,
      ease: ALFA_ANIMATION.ease.smooth,
      onUpdate: () => {
        displayValue.value = Math.round(displayValue.value)
      }
    })
  }

  return { displayValue, animate }
}

/**
 * Анимация модального окна
 */
export function useModalAnimation(
  overlayRef: Ref<HTMLElement | null>,
  contentRef: Ref<HTMLElement | null>
) {
  const animateIn = () => {
    if (prefersReducedMotion()) return

    const tl = gsap.timeline()
    
    if (overlayRef.value) {
      tl.from(overlayRef.value, {
        opacity: 0,
        duration: ALFA_ANIMATION.duration.quick,
        ease: ALFA_ANIMATION.ease.enter
      })
    }

    if (contentRef.value) {
      tl.from(contentRef.value, {
        y: 40,
        opacity: 0,
        scale: 0.95,
        duration: ALFA_ANIMATION.duration.enter,
        ease: ALFA_ANIMATION.ease.enter
      }, '-=0.15')
    }
  }

  const animateOut = () => {
    if (prefersReducedMotion()) return

    const tl = gsap.timeline()
    
    if (contentRef.value) {
      tl.to(contentRef.value, {
        y: 20,
        opacity: 0,
        scale: 0.98,
        duration: ALFA_ANIMATION.duration.exit,
        ease: ALFA_ANIMATION.ease.exit
      })
    }

    if (overlayRef.value) {
      tl.to(overlayRef.value, {
        opacity: 0,
        duration: ALFA_ANIMATION.duration.exit,
        ease: ALFA_ANIMATION.ease.exit
      }, '-=0.1')
    }
  }

  return { animateIn, animateOut }
}

/**
 * Анимация перехода между страницами
 */
export function usePageTransition(elementRef: Ref<HTMLElement | null>) {
  onMounted(() => {
    if (!elementRef.value || prefersReducedMotion()) return

    gsap.from(elementRef.value, {
      opacity: 0,
      y: 20,
      duration: ALFA_ANIMATION.duration.quick,
      ease: ALFA_ANIMATION.ease.enter
    })
  })
}

/**
 * Пульсирующая анимация для уведомлений/индикаторов
 */
export function usePulseAnimation(elementRef: Ref<HTMLElement | null>) {
  let animation: gsap.core.Tween | null = null

  onMounted(() => {
    if (!elementRef.value || prefersReducedMotion()) return

    animation = gsap.to(elementRef.value, {
      scale: 1.1,
      opacity: 0.8,
      duration: 0.8,
      ease: 'power2.inOut',
      repeat: -1,
      yoyo: true
    })
  })

  onBeforeUnmount(() => {
    animation?.kill()
  })

  return { animation }
}

/**
 * Скелетон-анимация для загрузки
 */
export function useSkeletonAnimation(elementRef: Ref<HTMLElement | null>) {
  onMounted(() => {
    if (!elementRef.value || prefersReducedMotion()) return

    gsap.to(elementRef.value, {
      opacity: 0.5,
      duration: 0.8,
      ease: 'power2.inOut',
      repeat: -1,
      yoyo: true
    })
  })
}

/**
 * Анимация успеха (галочка, чекмарк)
 */
export function useSuccessAnimation(elementRef: Ref<HTMLElement | null>) {
  const animate = () => {
    if (!elementRef.value || prefersReducedMotion()) return

    const tl = gsap.timeline()
    
    tl.from(elementRef.value, {
      scale: 0,
      duration: 0.3,
      ease: 'back.out(1.7)'
    })
    .to(elementRef.value, {
      scale: 1.2,
      duration: 0.15,
      ease: 'power2.out'
    })
    .to(elementRef.value, {
      scale: 1,
      duration: 0.15,
      ease: 'power2.in'
    })
  }

  return { animate }
}

/**
 * Анимация прогресс-бара
 */
export function useProgressAnimation(
  progressRef: Ref<HTMLElement | null>
) {
  const currentPercent = ref(0)

  const animate = (newPercent: number) => {
    if (prefersReducedMotion()) {
      currentPercent.value = newPercent
      return
    }

    gsap.to(currentPercent, {
      value: newPercent,
      duration: 1,
      ease: ALFA_ANIMATION.ease.smooth,
      onUpdate: () => {
        if (progressRef.value) {
          progressRef.value.style.width = `${currentPercent.value}%`
        }
      }
    })
  }

  return { currentPercent, animate }
}
