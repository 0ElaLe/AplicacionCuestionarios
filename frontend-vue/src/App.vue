<script setup lang="ts">
import { onMounted } from 'vue'
import { useApp }   from './composables/useApp'
import AppHeader    from './components/AppHeader.vue'
import AppFooter    from './components/AppFooter.vue'

const { init } = useApp()
onMounted(init)
</script>

<template>
  <AppHeader />
  <main class="app-main">
    <RouterView v-slot="{ Component }">
      <Transition name="view">
        <component :is="Component" />
      </Transition>
    </RouterView>
  </main>
  <AppFooter />
</template>

<style>
.view-enter-active { animation: fadeSlideUp 0.4s ease both; }
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
