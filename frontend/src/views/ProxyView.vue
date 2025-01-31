<script setup>
import { ref, computed, onMounted } from 'vue';
import { mdiAlert } from '@mdi/js';
import { useProxiesStore } from '@/store/proxyStore';

const proxiesStore = useProxiesStore();
const dialogAddEdit = ref(false);
const dialogDelete = ref(false);
const newProxy = ref({
  id: null,
  address: '',
  port: '',
  username: '',
  password: '',
});

onMounted(async () => {
  await proxiesStore.fetchProxies();
});

const openAddEditDialog = (proxy = null) => {
  if (proxy) {
    newProxy.value = { ...proxy };
  } else {
    newProxy.value = { id: null, address: '', port: '', username: '', password: '' };
  }
  dialogAddEdit.value = true;
};

const saveProxy = async () => {
  if (newProxy.value.id) {
    await proxiesStore.editProxy(newProxy.value);
  } else {
    await proxiesStore.addProxy(newProxy.value);
  }
  dialogAddEdit.value = false;
};

const showProxyDelete = (proxy) => {
    newProxy.value = proxy;
    dialogDelete.value = true
}

const deleteProxy = async (proxyId) => {
  await proxiesStore.deleteProxy(proxyId);
  dialogDelete.value = false;
};
</script>

<template>
  <v-sheet class="pa-6 mx-auto" >
    <div v-if="proxiesStore.loading">
      <v-progress-circular indeterminate></v-progress-circular>
    </div>
    <div v-else>
      <h1>Прокси</h1>
      <v-btn color="primary" @click="openAddEditDialog">Добавить прокси</v-btn>
      <v-divider class="my-4"></v-divider>

      <div v-if="proxiesStore.proxyList.length === 0">
        Список прокси пуст.
      </div>

      <v-list>
        <v-list-item v-for="proxy in proxiesStore.proxyList" :key="proxy.id">
          <v-list-item-content>
            <v-list-item-title>{{ proxy.address }}:{{ proxy.port }}</v-list-item-title>
            <v-list-item-subtitle>{{ proxy.username || 'Без аутентификации' }}</v-list-item-subtitle>
          </v-list-item-content>
          <v-list-item-actions>
            <div style="display: flex; justify-content: space-between;">
                <v-btn color="orange"  @click="openAddEditDialog(proxy)">Редактировать</v-btn>
                <v-btn color="red"  @click="showProxyDelete(proxy)">Удалить</v-btn>
                <v-btn color="green"  :loading="proxiesStore.loadingCheck" @click="proxiesStore.checkProxy(proxy.id)">Проверить</v-btn>
            </div>
          </v-list-item-actions>
        </v-list-item>
      </v-list>

      <!-- Add/Edit Dialog -->
      <v-dialog v-model="dialogAddEdit" max-width="500">
        <v-card>
          <v-card-title>{{ newProxy.id ? 'Редактировать' : 'Добавить' }} прокси</v-card-title>
          <v-card-text>
            <v-text-field v-model="newProxy.address" label="Адрес" required></v-text-field>
            <v-text-field v-model="newProxy.port" label="Порт" required></v-text-field>
            <v-text-field v-model="newProxy.username" label="Логин"></v-text-field>
            <v-text-field v-model="newProxy.password" label="Пароль" type="password"></v-text-field>
          </v-card-text>
          <v-card-actions>
            <v-btn color="primary" @click="saveProxy">Сохранить</v-btn>
            <v-btn text @click="dialogAddEdit = false">Отмена</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Delete Confirmation Dialog -->
      <v-dialog v-model="dialogDelete" max-width="400">
        <v-card>
          <v-card-title>Удалить прокси?</v-card-title>
          <v-card-text>Вы уверены, что хотите удалить этот прокси?</v-card-text>
          <v-card-actions>
            <v-btn color="red" @click="deleteProxy(newProxy.id)">Удалить</v-btn>
            <v-btn text @click="dialogDelete = false">Отмена</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div>
  </v-sheet>
</template>

<style scoped>
.pa-6 {
  padding: 24px;
}
.mx-auto {
  margin: auto;
}
</style>
