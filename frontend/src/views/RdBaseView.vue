
<script setup>
import { useRdBaseStore } from '@/store/rdBaseStore.js';
import { useTgStore } from '@/store/tgStore';
import { onMounted } from 'vue';

const rdBaseStore = useRdBaseStore();
// const telegramStore = useTgStore();

// const updateSelectedAccount = async () => {
//     await telegramStore.getAccInfo();
// }

// onMounted(async () => {
//     // await rdBaseStore.loadItems();
//     await telegramStore.getAccountsList();
// })

document.title = "RD База";
</script>

<template>
    
        
    <v-sheet
        class="pa-6 text-white mx-auto  mb-4"
        width="100%"
        rounded
    >
    <h1 class="mb-4">Просмотр RD Базы</h1>

    <div v-if="rdBaseStore.loading" class="mt-4">
        <v-progress-circular :size="50" class="mb-4" indeterminate></v-progress-circular>
    </div>
    <!-- <div v-else class="mt-5">
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
        </div> -->
        <!-- <div v-if="telegramStore.accountData !== null" class="mt-4"> -->
            <v-data-table-server
                v-model:items-per-page="rdBaseStore.itemsPerPagee"
                :headers="rdBaseStore.headers"
                :items="rdBaseStore.serverItems"
                :items-length="rdBaseStore.totalItems"
                :loading="rdBaseStore.loading"
                :search="rdBaseStore.search"
                item-value="name"
                @update:options="rdBaseStore.loadItems"
            >
                <template v-slot:tfoot>
                <tr>
                    <td>
                    <v-text-field variant="outlined" type='text' v-model="rdBaseStore.userId" class="ma-2" density="compact" placeholder="User ID" hide-details></v-text-field>
                    </td>
                </tr>
                </template>
            </v-data-table-server>
        <!-- </div> -->
    <!-- </div> -->
    </v-sheet>
</template>

