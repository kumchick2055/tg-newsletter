import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';
import { inferRuntimeType } from 'vue/compiler-sfc';


const apiUrl = import.meta.env.VITE_APIURL;

export const useTgStore = defineStore('tgStore', () => {
  const isLoading = ref(false);
  const isLoadingAuth = ref(false);
  const detailsError = ref('');
  const fullDetailError = ref('');


  const accountData = ref(null);

  const apiId = ref('');
  const apiHash = ref('');
  const phone = ref('');
  const password = ref('');

  const smsCode = ref('');

  const accountsList = ref([]);
  const selectedAccount = ref(null);

  const tmpKey = ref(null);



  const getAccInfo = async () => {
      isLoading.value = true;
      accountData.value = null;

      try{
          const req = await axios.get(`${apiUrl}/api/v1/telethon/get_tg_acc_info`, {
            params: {
                user_id: selectedAccount.value
            }
          });      
          if(req.data?.status === 'fail'){
            detailsError.value = req.data.detail;
          } else {
              accountData.value = req.data?.detail;
          }

          isLoading.value = false;
          return req.data;
      } catch {
        isLoading.value = false;
      } finally {
        isLoading.value = false;
      }
      
      return {'error': true};

  }


  const getAccountsList = async () => {
        isLoading.value = true;

        try{
            const res = await axios.get(`${apiUrl}/api/v1/telethon/get_accounts_list`);

            if(res.data){
                accountsList.value = res.data;
            }
        }
        catch {
            
        } finally {
            isLoading.value = false;
        }
  }

  const exitTgSession = async () => {
    isLoading.value = true;

    try {
        const req = await axios.delete(`${apiUrl}/api/v1/telethon/exit_from_account`, {
            params: {
                user_id: selectedAccount.value
            }
        });

        if(req.data?.status === 'ok'){
            accountData.value = null;
            selectedAccount.value = '';
            detailsError.value = '';
            await getAccountsList();
        }


    } catch {
        isLoading.value = false;
        return false;
    } finally {
        isLoading.value = false;
    }

    return true;
  }

  // Создание новой сессии
  const createTgSession = async () => {
    isLoading.value = true;

    try {
        const req = await axios.post(`${apiUrl}/api/v1/telethon/create_tg_session`, {
            'api_id': apiId.value,
            'api_hash': apiHash.value
        });

        if(req.data?.status === 'fail'){
            detailsError.value = req.data.detail;
            tmpKey.value = req.data.tmp_key;
        } else {
            accountData.value = req.data?.detail;
        }

        return req.data;
    } catch {

    } finally {
        isLoading.value = false;
    }
  }

  // Отправка номера телефона
  const sendPhoneData = async () => {
    isLoading.value = true;
    fullDetailError.value = '';

    console.log(tmpKey.value);

    try {
        const req = await axios.post(`${apiUrl}/api/v1/telethon/send_phone_tg`, {
            'phone': phone.value
        }, {
            params: {
                "user_id": tmpKey.value
            }
        });

        if(req.data?.status === 'fail'){
            detailsError.value = req.data.detail;
        } else {
            accountData.value = req.data?.detail;
        }

        if(req.data?.full_detail){
            fullDetailError.value = req.data.full_detail;
        }

        return req.data;
    } catch {

    } finally {
        isLoading.value = false;
    }
  }

  // Отправка номера телефона
  const sendPasswordData = async () => {
    isLoading.value = true;
    fullDetailError.value = '';

    try {
        const req = await axios.post(`${apiUrl}/api/v1/telethon/send_password_tg`, {
            'password': password.value
        },{
            params: {
                "user_id": tmpKey.value
            }
        });

        if(req.data?.status === 'fail'){
            detailsError.value = req.data.detail;

            
        } else {
            accountData.value = req.data?.detail;
            detailsError.value = '';
            tmpKey.value = null;
            alert('Аккаунт успешно добавлен');
            await getAccountsList();
        }

        if(req.data?.full_detail){
            fullDetailError.value = req.data.full_detail;
        }

        return req.data;
    } catch {

    } finally {
        isLoading.value = false;
    }
  }

  // Отправка кода из смс
  const sendSmsCode = async () => {
    isLoading.value = true;
    fullDetailError.value = '';

    try {
        const req = await axios.post(`${apiUrl}/api/v1/telethon/send_smscode_tg`, {
            'code': smsCode.value
        },{
            params: {
                "user_id": tmpKey.value
            }
        });

        if(req.data?.status === 'fail'){
            detailsError.value = req.data.detail;
        } else {
            accountData.value = req.data?.detail;

            // if(accountData.value.length > 0){   
                detailsError.value = '';
                tmpKey.value = null;
                alert('Аккаунт успешно добавлен');
                await getAccountsList();
            // }
        }

        if(req.data?.full_detail){
            fullDetailError.value = req.data.full_detail;
        }

        return req.data;
    } catch {

    } finally {
        isLoading.value = false;
    }
  }


  return {
    getAccInfo,
    createTgSession,
    sendPhoneData,
    sendSmsCode,
    sendPasswordData,
    exitTgSession,

    isLoading,
    isLoadingAuth,
    accountData,
    detailsError,
    fullDetailError,

    apiId,
    apiHash,
    phone,
    password,
    smsCode,

    accountsList,
    getAccountsList,
    selectedAccount
  };
});