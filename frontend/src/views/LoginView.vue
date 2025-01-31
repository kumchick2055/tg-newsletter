
<script setup>
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/authStore';

import { mdiLockOutline,mdiAccount } from '@mdi/js';
import { ref } from 'vue';

document.title = "Авторизация";

const router = useRouter()

const auth = useAuthStore();

const showError = ref(false);

const authorization = async () => {
    const data = await auth.authorization();

    if(data?.access_token){
        localStorage.setItem('user', JSON.stringify({'token': data.access_token}));
        router.push('/');
    } else {
      showError.value = true;
    }
}
</script>


<template>
  <v-app>
    <div class="mt-16">
    <v-card
      class="mx-auto pa-12 pb-8 "
      elevation="8"
      max-width="448"
      rounded="lg"
    >
      <div class="text-subtitle-1 text-medium-emphasis">Account</div>

      <v-text-field
        v-model="auth.login"
        density="compact"
        placeholder="Login"
        :prepend-inner-icon="mdiAccount"
        variant="outlined"
      ></v-text-field>

      <div class="text-subtitle-1 text-medium-emphasis d-flex align-center justify-space-between">
        Password
      </div>

      <v-text-field
        v-model="auth.password"
        type="password"
        density="compact"
        placeholder="Enter your password"
        :prepend-inner-icon="mdiLockOutline"
        variant="outlined"
        @click:append-inner="visible = !visible"
      ></v-text-field>


      <v-btn
        class="mb-8"
        color="blue"
        size="large"
        variant="tonal"
        block
        @click="authorization()"
        :loading='auth.isLoading'
        :disabled="auth.isLoading || (auth.login.length === 0 || auth.password.length === 0)"
      >
        Log In
      </v-btn>

      <div v-if="showError">
        <v-alert closable v-on:click:close="showError = false" text="Authorization error" type="error" variant="tonal"></v-alert>
      </div>

    </v-card>
  </div>
  </v-app>
</template>
