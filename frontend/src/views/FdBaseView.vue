<template>
    <v-app>
        <v-sheet
            class="pa-6 text-white mx-auto  mb-4"
            width="100%"
            rounded
          >
          <h1 class="mb-4">Просмотр FD Базы</h1>
          <v-data-table-server
              v-model:items-per-page="fdBaseStore.itemsPerPagee"
              :headers="fdBaseStore.headers"
              :items="fdBaseStore.serverItems"
              :items-length="fdBaseStore.totalItems"
              :loading="fdBaseStore.loading"
              :search="fdBaseStore.search"
              item-value="name"
              @update:options="fdBaseStore.loadItems"
          >
              <template v-slot:tfoot>
              <tr>
                  <td>
                  <v-text-field variant="outlined" type='text' v-model="fdBaseStore.userId" class="ma-2" density="compact" placeholder="User ID" hide-details></v-text-field>
                  </td>
              </tr>
              </template>
          </v-data-table-server>
        </v-sheet>
    </v-app>
</template>


<script setup>
import { useFdBaseStore } from '@/store/fdBaseStore';


const fdBaseStore = useFdBaseStore();
document.title = "FD База";
</script>