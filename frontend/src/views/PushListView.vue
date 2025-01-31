<script setup>
  import {usePushListStore} from '@/store/pushListStore.js';
import { useTgStore } from '@/store/tgStore';
import { mdiAlert } from '@mdi/js';
  import {onMounted, ref} from 'vue';
  

  const pushListStore = usePushListStore();
  const telegramStore = useTgStore();
  const deletePush = ref(false);
  const deletePushId = ref(null);

  const selectSort = async () => {
    await pushListStore.fetchPushList(telegramStore.selectedAccount)
  }

  const deletePushModal = async (id) => {
    deletePushId.value = id;
    deletePush.value = true;
  }

  const executeDeletePush = async () => {
    const res = await pushListStore.deletePushList(deletePushId.value);

    if(res){
      await pushListStore.fetchPushList(telegramStore.selectedAccount);
    }
    deletePush.value = false;
    deletePushId.value = null;
  }

  onMounted(async () => {
    if(telegramStore.selectedAccount === null){
      await telegramStore.getAccountsList();
    }
  });

  const updateSelectedAccount = async () => {
    await telegramStore.getAccInfo();
    await pushListStore.fetchPushList(telegramStore.selectedAccount);
  }

  const formatIsoToCustom = (isoString) => {
    const dateObj = new Date(isoString);
    const hours = dateObj.getHours().toString().padStart(2, '0');
    const minutes = dateObj.getMinutes().toString().padStart(2, '0');
    const year = dateObj.getFullYear();
    const month = (dateObj.getMonth() + 1).toString().padStart(2, '0');
    const day = dateObj.getDate().toString().padStart(2, '0');

    return `${hours}:${minutes} ${year}-${month}-${day}`;
}

  document.title = "Пуши";
</script>


<template>
  <v-dialog
      v-model="deletePush"
      width="auto"
    >
      <v-card
        max-width="400"
        :prepend-icon="mdiAlert"
        text="Удалить пуш?"
        title="Предупреждение"
      >
        <template v-slot:actions>
          <v-btn
            text="Да"
            :loading="pushListStore.loading"
            @click.native="executeDeletePush"
          ></v-btn>
          <v-btn
            text="Нет"
            :loading="pushListStore.loading"
            @click="deletePush = false"
          ></v-btn>
        </template>
      </v-card>
  </v-dialog>

    <v-sheet
    class="pa-6 text-white mx-auto"
    width="100%"
    rounded
  >
  <div>
    <h4 class="text-h5 font-weight-bold mb-4">Список пушей</h4>
    <v-divider></v-divider>
  </div>
  <div v-if="pushListStore.loading || telegramStore.isLoading" class="mt-4">
    <v-progress-circular :size="50" class="mb-4" indeterminate></v-progress-circular>
  </div>
  <div v-else class="mt-5">
    <div class="mt-4">
      <v-select
      label="Аккаунт"
      :items="telegramStore.accountsList.map(i => i.account_id)"
      v-model="telegramStore.selectedAccount"
      v-on:update:model-value="updateSelectedAccount"
      variant="outlined"
    ></v-select> 
    </div>
    
    <div v-if="telegramStore.accountData !== null">
      <div class="mb-2">
        Информация об аккаунте:
      </div>
      <div class="mb-4">
        <div>
          Id: {{ telegramStore.accountData.user_id }}
        </div>
        <div>
          Юзернейм: {{ telegramStore.accountData.username }}
        </div>
        <div>
          Имя: {{ telegramStore.accountData.fullname }}
        </div>
      </div>
    </div>
    <div v-else class="mb-2 mb-4">
        Аккаунт не доступен.
    </div>
    <div v-if="telegramStore.accountData !== null" class="mt-4">
      <v-divider class="mb-4"></v-divider>

      <v-select
      label="Статус пушей"
      :items="[
        'В ожидании',
        'Завершенные'
      ]"
      v-model="pushListStore.selectedSortValue"
      v-on:update:model-value="selectSort"
      variant="outlined"
    ></v-select> 

      <div v-for="item in pushListStore.pushList">
        <!-- {{item.name}} -->
        <v-card
          :title="item.name"
          :subtitle="item.job_id"
          :text="`
Время отправки: ${formatIsoToCustom(item.date_push)} ${item.timezone}
`"
          variant="tonal"
          class="mb-4"
        >
          <v-card-actions v-if="pushListStore.selectedSortValue !== 'Завершенные'">
            <v-btn color="red" @click.native="deletePushModal(item.id)">Удалить</v-btn>
          </v-card-actions>
        </v-card>
      </div>

    </div>
    <div v-else>
      <v-alert text="Для просмотра выберите аккаунт." type='info'></v-alert>
    </div>

  </div>
  </v-sheet>
</template>
