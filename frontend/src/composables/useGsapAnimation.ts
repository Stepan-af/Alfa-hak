import { onBeforeUnmount, Ref } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export interface AnimationOptions {
  duration?: number
  delay?: number
  ease?: string
  stagger?: number
}

export const useGsapAnimation = () => {
  const animations: gsap.core.Tween[] = []

  // Fade in from bottom
  const fadeInUp = (
    target: string | Element | Ref<Element | undefined>,
    options: AnimationOptions = {}
  ) => {
    const tween = gsap.from(target, {
      y: 50,
      opacity: 0,
      duration: options.duration || 0.8,
      delay: options.delay || 0,
      ease: options.ease || 'power3.out',
      stagger: options.stagger
    })
    animations.push(tween)
    return tween
  }

  // Fade in from left
  const fadeInLeft = (
    target: string | Element | Ref<Element | undefined>,
    options: AnimationOptions = {}
  ) => {
    const tween = gsap.from(target, {
      x: -50,
      opacity: 0,
      duration: options.duration || 0.8,
      delay: options.delay || 0,
      ease: options.ease || 'power3.out',
      stagger: options.stagger
    })
    animations.push(tween)
    return tween
  }

  // Fade in from right
  const fadeInRight = (
    target: string | Element | Ref<Element | undefined>,
    options: AnimationOptions = {}
  ) => {
    const tween = gsap.from(target, {
      x: 50,
      opacity: 0,
      duration: options.duration || 0.8,
      delay: options.delay || 0,
      ease: options.ease || 'power3.out',
      stagger: options.stagger
    })
    animations.push(tween)
    return tween
  }

  // Scale in
  const scaleIn = (
    target: string | Element | Ref<Element | undefined>,
    options: AnimationOptions = {}
  ) => {
    const tween = gsap.from(target, {
      scale: 0.8,
      opacity: 0,
      duration: options.duration || 0.6,
      delay: options.delay || 0,
      ease: options.ease || 'back.out(1.7)',
      stagger: options.stagger
    })
    animations.push(tween)
    return tween
  }

  // Scroll-triggered animation
  const scrollAnimation = (
    target: string | Element | Ref<Element | undefined>,
    animationProps: gsap.TweenVars,
    scrollTriggerOptions: ScrollTrigger.Vars = {}
  ) => {
    const resolvedTarget = target instanceof Object && 'value' in target ? target.value : target
    if (!resolvedTarget) return null
    
    const tween = gsap.from(resolvedTarget, {
      ...animationProps,
      scrollTrigger: {
        trigger: resolvedTarget,
        start: 'top 80%',
        end: 'bottom 20%',
        toggleActions: 'play none none reverse',
        ...scrollTriggerOptions
      }
    })
    animations.push(tween)
    return tween
  }

  // Hover animation
  const hoverScale = (
    target: string | Element | Ref<Element | undefined>,
    scale: number = 1.05
  ) => {
    const element = typeof target === 'string' ? document.querySelector(target) : target

    if (element) {
      const handleMouseEnter = () => {
        gsap.to(element, {
          scale,
          duration: 0.3,
          ease: 'power2.out'
        })
      }

      const handleMouseLeave = () => {
        gsap.to(element, {
          scale: 1,
          duration: 0.3,
          ease: 'power2.out'
        })
      }

      if (element instanceof Element) {
        element.addEventListener('mouseenter', handleMouseEnter)
        element.addEventListener('mouseleave', handleMouseLeave)
      }

      return {
        destroy: () => {
          if (element instanceof Element) {
            element.removeEventListener('mouseenter', handleMouseEnter)
            element.removeEventListener('mouseleave', handleMouseLeave)
          }
        }
      }
    }
  }

  // Stagger animation for lists
  const staggerAnimation = (
    targets: string,
    options: AnimationOptions = {}
  ) => {
    const tween = gsap.from(targets, {
      y: 30,
      opacity: 0,
      duration: options.duration || 0.6,
      ease: options.ease || 'power3.out',
      stagger: options.stagger || 0.1
    })
    animations.push(tween)
    return tween
  }

  // Cleanup on unmount
  onBeforeUnmount(() => {
    animations.forEach(anim => anim.kill())
    ScrollTrigger.getAll().forEach(trigger => trigger.kill())
  })

  return {
    fadeInUp,
    fadeInLeft,
    fadeInRight,
    scaleIn,
    scrollAnimation,
    hoverScale,
    staggerAnimation
  }
}
