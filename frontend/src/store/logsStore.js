import axios from "axios";
import { defineStore } from "pinia";
import { ref } from "vue";


const apiUrl = import.meta.env.VITE_APIURL;



function sortByDate(list) {
    return list.sort((a, b) => {
        const dateA = a.split('.')[0];
        const dateB = b.split('.')[0];
        const [dayA, monthA, yearA] = dateA.split('_');
        const [dayB, monthB, yearB] = dateB.split('_');

        const fullDateB = new Date(`${yearA}-${monthA}-${dayA}`);
        const fullDateA = new Date(`${yearB}-${monthB}-${dayB}`);

        // Сравниваем две даты
        return fullDateA - fullDateB;
    });
}

// /api/v1/get_files_logs
export const useLogsStore = defineStore('logsStore', () => {
    const loading = ref(false);
    const logsList = ref([]);
    const loadingDelete = ref(false);
    
    const getLogsFiles = async () => {
        loading.value = true;

        try{
            const res = await axios.get(`${apiUrl}/api/v1/logs/get_files_logs`)

            logsList.value = sortByDate(res.data);
        } catch {

        } finally {
            loading.value = false
        }
    };


    const deleteLogsFiles = async () => {
        loadingDelete.value = true;

        try{
            const res = await axios.delete(`${apiUrl}/api/v1/logs/delete_logs`)

            if(res.data?.status === 'ok'){
                await getLogsFiles()
            }
        } catch {

        } finally {
            loadingDelete.value = false
        }
    };

    return {
        loading,
        getLogsFiles,
        deleteLogsFiles,
        loadingDelete,
        logsList
    };
})