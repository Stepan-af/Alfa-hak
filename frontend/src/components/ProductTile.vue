<template>
  <v-card
    :to="to"
    :href="href"
    class="product-tile"
    :class="{ 'product-tile--animated': animated }"
    elevation="2"
    rounded="lg"
  >
    <div v-if="image" class="product-tile__image">
      <v-img
        :src="image"
        :alt="title"
        height="200"
        cover
      >
        <template v-slot:placeholder>
          <div class="d-flex align-center justify-center fill-height">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
          </div>
        </template>
      </v-img>
      <div v-if="badge" class="product-tile__badge">
        <v-chip :color="badgeColor" size="small">
          {{ badge }}
        </v-chip>
      </div>
    </div>

    <v-card-text class="pa-6">
      <div class="product-tile__header mb-4">
        <v-icon
          v-if="icon && !image"
          :icon="icon"
          :color="iconColor"
          size="48"
          class="mb-3"
        ></v-icon>
        <h3 class="product-tile__title text-h5 font-weight-bold mb-2">
          {{ title }}
        </h3>
        <p v-if="category" class="product-tile__category text-caption text-medium-emphasis mb-2">
          {{ category }}
        </p>
      </div>

      <p class="product-tile__description text-body-2 mb-4">
        <slot>{{ description }}</slot>
      </p>

      <div v-if="features && features.length" class="product-tile__features mb-4">
        <v-chip
          v-for="(feature, index) in features"
          :key="index"
          size="small"
          variant="tonal"
          class="mr-2 mb-2"
        >
          {{ feature }}
        </v-chip>
      </div>

      <div v-if="price || $slots.footer" class="product-tile__footer">
        <slot name="footer">
          <div v-if="price" class="product-tile__price">
            <span class="text-h6 font-weight-bold text-primary">
              {{ formattedPrice }}
            </span>
            <span v-if="priceUnit" class="text-caption text-medium-emphasis ml-1">
              {{ priceUnit }}
            </span>
          </div>
        </slot>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title: string
  description?: string
  category?: string
  icon?: string
  iconColor?: string
  image?: string
  badge?: string
  badgeColor?: string
  price?: number | string
  priceUnit?: string
  features?: string[]
  to?: string
  href?: string
  animated?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  iconColor: 'primary',
  badgeColor: 'success',
  animated: true
})

const formattedPrice = computed(() => {
  if (typeof props.price === 'number') {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 0
    }).format(props.price)
  }
  return props.price
})
</script>

<style scoped>
.product-tile {
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
}

.product-tile--animated:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 32px rgba(239, 49, 36, 0.2) !important;
  border-color: var(--v-theme-primary);
}

.product-tile__image {
  position: relative;
  overflow: hidden;
}

.product-tile__image :deep(.v-img) {
  transition: transform 0.4s ease;
}

.product-tile--animated:hover .product-tile__image :deep(.v-img) {
  transform: scale(1.05);
}

.product-tile__badge {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 1;
}

.product-tile__header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.product-tile__title {
  line-height: 1.3;
}

.product-tile__category {
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
}

.product-tile__description {
  opacity: 0.9;
  line-height: 1.6;
}

.product-tile__features {
  display: flex;
  flex-wrap: wrap;
}

.product-tile__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.product-tile__price {
  display: flex;
  align-items: baseline;
}
</style>
