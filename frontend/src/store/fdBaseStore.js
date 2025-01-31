import { defineStore } from "pinia";
import { ref } from "vue";
import axios from "axios";
import { watch } from "vue";

const apiUrl = import.meta.env.VITE_APIURL;

export const useFdBaseStore = defineStore('fdBase', () => {
    const itemsPerPagee = ref(10);
    const search = ref('');
    const loading = ref(true);
    const totalItems = ref(0);
    const serverItems = ref([]);
    const userId = ref('');

    watch(userId, (newUserId) => {
        search.value = String(Date.now());
    });


    const loadItems = async ({page, itemsPerPage, sortBy, search}) => {
      loading.value = true;

      let sendParams = {
        limit: itemsPerPage,
        skip: (page - 1) * itemsPerPage,
      };
      if(userId.value) sendParams['user_id'] = userId.value;
      
      try{
        const res = await axios.get(`${apiUrl}/api/v1/dbusers/fdusers/search`, {
            params: sendParams
        });

        serverItems.value = res.data.users;
        totalItems.value = res.data.total;

      } catch (e) {

      } finally {
        loading.value = false;
      }

    };


    const headers = ref([
        {
            title: 'ID',
            align: 'start',
            sortable: false,
            key: 'id'
        },
        {
            title: 'User ID',
            align: 'start',
            sortable: false,
            key: 'user_id'
        },
        {
            title: 'Username',
            align: 'start',
            sortable: false,
            key: 'username'
        },
        {
            title: 'Time Create',
            align: 'start',
            sortable: false,
            key: 'date_create'
        },
    ]);

    return {
        headers,
        itemsPerPagee,
        userId,

        search, 
        loading,
        totalItems,
        serverItems,

        loadItems
    };
});
