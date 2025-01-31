import {defineStore} from  "pinia";
import {ref, watch} from "vue";
import axios from "axios";


const apiUrl = import.meta.env.VITE_APIURL;


export const usePushListStore = defineStore('pushListStore', () => {
  const loading = ref(false);
  const pushList = ref([]);
  const selectedSortValue = ref('В ожидании');

  const fetchPushList = async (user_id) => {
    loading.value = true;
    let selectedSortValueReq = '';
    if(selectedSortValue.value === 'В ожидании'){
      selectedSortValueReq = 'wait';
    }
    if(selectedSortValue.value === 'Завершенные'){
      selectedSortValueReq = 'finished';
    }

    try {
      const res = await axios.get(`${apiUrl}/api/v1/push/get_all`, {
        params: {
          'user_id': user_id,
          'status': selectedSortValueReq
        }
      });

      // if(res.data?.status === 'ok'){
        pushList.value = res.data;
      // }
    } catch (e) {

    } finally {
      loading.value = false;
    }
  }

  const deletePushList = async(push_id) => {
    loading.value = true;

    try {
      const res = await axios.delete(`${apiUrl}/api/v1/push/delete_push`, {
        params: {
          'push_id':  push_id
        }
      })

      if(res.data?.status === 'ok'){
        return true;
      }
    } catch (error) {
      
    } finally{
      loading.value = false;
    }
  }


  return {
    loading,
    pushList,
    selectedSortValue,
    deletePushList,

    fetchPushList
  };
})
