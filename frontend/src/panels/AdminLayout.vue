<template>
    <v-app>
      <v-navigation-drawer v-model="drawer" :rail="rail" @click="rail = false" permanent width="256" location="left">
        <template v-slot:prepend>
          <v-list-item
            lines="two"
            :prepend-icon="mdiAccount"
            subtitle="Logged in"
            :title="userName"
          >
            <template v-slot:append>
              <v-btn
                :icon="mdiChevronLeft"
                variant="text"
                @click.stop="rail = !rail"
              ></v-btn>
            </template>
          </v-list-item>
        </template>
  
        <v-divider></v-divider>
  
        <v-list dense>
          <v-list-item :prepend-icon="mdiHome" link @click="navigateTo('/settings')">
            <v-list-item-title>Главная</v-list-item-title>
          </v-list-item>

          <v-list-item :prepend-icon="mdiAccountMultiple" link @click="navigateTo('/telegram_accounts')">
            <v-list-item-title>TG Аккаунты</v-list-item-title>
          </v-list-item>

          <v-list-item :prepend-icon="mdiBellBadge" link @click="navigateTo('/push_list')">
            <v-list-item-title>Пуши</v-list-item-title>
          </v-list-item>
  
          <v-list-item :prepend-icon="mdiArchive" link @click="navigateTo('/rd-base')">
            <v-list-item-title>RD база</v-list-item-title>
          </v-list-item>
  
          <v-list-item :prepend-icon="mdiForum" link @click="navigateTo('/fd-base')">
            <v-list-item-title>FD база</v-list-item-title>
          </v-list-item>

          <v-list-item :prepend-icon="mdiNoteMultiple" link @click="navigateTo('/logs')">
            <v-list-item-title>Логи</v-list-item-title>
          </v-list-item>

          <v-list-item :prepend-icon="mdiNoteMultiple" link @click="navigateTo('/proxy')">
            <v-list-item-title>Прокси</v-list-item-title>
          </v-list-item>
        </v-list>
  
        <template v-slot:append>
          <div class="pa-2">
            <v-btn :class="rail ? 'd-none' : ''" @click="logout()" block>
              Выйти
            </v-btn>
          </div>
        </template>
      </v-navigation-drawer>
  
      <v-main>
        <v-container>
          <RouterView></RouterView>
        </v-container>
      </v-main>
    </v-app>
  </template>
  
    
  <script setup>
  import { useRouter } from 'vue-router';
  import { useAuthStore } from '../store/authStore';
  import { mdiAccount, mdiChevronLeft, mdiHome, mdiForum, mdiArchive, mdiNoteMultiple, mdiBellBadge, mdiAccountMultiple } from '@mdi/js';
  import { ref } from 'vue';
  
  const router = useRouter();
  const auth = useAuthStore();
  const userName = JSON.parse(atob(JSON.parse(localStorage.getItem('user')).token.split('.')[1])).sub;
  
  const rail = ref(false);
  const drawer = ref(true);
  
  const logout = () => {
  if(auth.logout())
      router.push('/login');
  }


  const navigateTo = (val) => {
    router.push(val);
  }
  
  </script>
  