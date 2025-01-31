<script setup>
import { useRouter } from 'vue-router';
const router = useRouter();

router.push(location.pathname);
</script>


<template>
  <RouterView/>
</template>
