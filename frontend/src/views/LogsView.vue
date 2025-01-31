<script setup>
import { useLogsStore } from '@/store/logsStore';
import { onMounted } from 'vue';
import { ref } from 'vue';
import { mdiAlert } from '@mdi/js';

const apiUrl = import.meta.env.VITE_APIURL;


const logsStore = useLogsStore();

onMounted(async () => {
    await logsStore.getLogsFiles()
})
const goToUrl = (url) => {
    window.open(url);
}
const dialogDelete = ref(false);



const deleteFiles = async () => {
    await logsStore.deleteLogsFiles();
    dialogDelete.value  = false;
}
</script>

<template>    
    <v-dialog
      v-model="dialogDelete"
      width="auto"
    >
      <v-card
        max-width="400"
        :prepend-icon="mdiAlert"
        text="При удалении стираются все логи. Продолжить?"
        title="Предупреждение"
      >
        <template v-slot:actions>
          <v-btn
            text="Да"
            :loading="logsStore.loadingDelete"
            @click="deleteFiles"
          ></v-btn>
          <v-btn
            text="Нет"
            :loading="logsStore.loadingDelete"
            @click="dialogDelete = false"
          ></v-btn>
        </template>
      </v-card>
    </v-dialog>


    <v-sheet
        class="pa-6 text-white mx-auto  mb-4"
        width="100%"
        rounded
        >
        <div v-if="logsStore.loading">
            <div class="mt-2">
                <v-progress-circular :size="50" indeterminate></v-progress-circular>
            </div>
        </div>
        <div v-else>
            <h1 class="mb-4">Логи</h1>
            <v-divider></v-divider>
            <div class="mt-2">
                <div class="mb-2">
                    Действия:
                    <v-btn @click.native="dialogDelete = true" color="red" variant="outlined" class="mt-2" block>
                        Очистить
                    </v-btn>
    
                </div>
                <v-divider></v-divider>
                <div class="mt-4">
                    <div v-if="logsStore.logsList.length === 0">
                        Список логов пустой :(
                    </div>
                    <div v-else>
                        <v-btn class="mt-4" v-for="item in logsStore.logsList" @click.native="goToUrl(apiUrl + '/static/logs/' + item)" :key="item" block>
                            {{ item }}
                        </v-btn>
                    </div>
                </div>
            </div>
        </div>
    </v-sheet>
</template>