<template>
  <div ref="cardRef" class="glass-card p-6 transform-gpu transition-all">
    <slot></slot>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import VanillaTilt from 'vanilla-tilt';

const cardRef = ref(null);

onMounted(() => {
  VanillaTilt.init(cardRef.value, {
    max: 10,
    speed: 400,
    glare: true,
    "max-glare": 0.2,
  });
});
</script>