<script setup>
import { proxyRefs, ref } from 'vue';
import { onMounted } from 'vue';
import { useTgStore } from '@/store/tgStore';
import axios from 'axios';
import { mdiAlert, mdiClockTimeFourOutline } from '@mdi/js';
import { timezoneList } from '@/store/timezones';
import moment from 'moment-timezone';
import { useProxiesStore } from '@/store/proxyStore';

// mdi-clock-time-four-outline
document.title = "Главная";



const proxiesStore = useProxiesStore();

const exitFromAccount = ref(false);

const telegramStore = useTgStore();
const isLoadingPush = ref(false);

const logsTelethonProgram = ref('');

const apiUrl = import.meta.env.VITE_APIURL;
const wsUrl = import.meta.env.VITE_WSURL;

// Подклюение к серверу вебсокета (логи)
const socket = new WebSocket(wsUrl);

socket.addEventListener('message', (event) => {
  logsTelethonProgram.value += event.data + '\n';
});

const checkPushMessageFailData = ref('');

const namePush = ref('');
const selectedProxy = ref(null);
const isUseProxy = ref(false);
const timezoneSelect = ref('Europe/Moscow')
const datePush = ref(null);
const menu2 = ref(false);
const timePush = ref(null);

const limitSpeed = ref('Без ограничений');
const limitSpeedValue = ref('max');

const onLimitSpeedupdate = (e) => {
  switch(e){
    case 'Минимальная':
      limitSpeedValue.value = 'min';
      break;
    case 'Средняя':
      limitSpeedValue.value = 'medium';
      break;
    case 'Медленная':
      limitSpeedValue.value = 'slow';
      break;
    default:
      limitSpeedValue.value = 'max';
      break;
  }
}

const toUnixTimestamp = (date) => {
    // Преобразуем объект Date в Unix время в секундах
    return Math.floor(date.getTime() / 1000);
}


const validateDateTime = (e) => {
  const now = new Date();
  now.setHours(0, 0, 0, 0);

  if(toUnixTimestamp(e) < toUnixTimestamp(now)){
    alert('Нельзя выбрать дату меньше сегодняшней')
  } else {
    datePush.value = e;
  }
}


function pad(number) {
  if (number < 10) {
    return "0" + number;
  }
  return number;
}

const toIsoStringWithoutUtc = (date) => {
  return (
      date.getFullYear() +
      "-" +
      pad(date.getMonth() + 1) +
      "-" +
      pad(date.getDate()) +
      "T" +
      pad(date.getHours()) +
      ":" +
      pad(date.getMinutes()) +
      ":" +
      pad(date.getSeconds()) +
      "." +
      (date.getMilliseconds() / 1000).toFixed(3).slice(2, 5)
  );
}



const combineCurrentTime = () => {
    const currentDate = new Date(); // Получаем текущее время
    const dateString = `${currentDate.getFullYear()}-${(currentDate.getMonth() + 1).toString().padStart(2, '0')}-${currentDate.getDate().toString().padStart(2, '0')}`;
    const timeString = `${currentDate.getHours().toString().padStart(2, '0')}:${currentDate.getMinutes().toString().padStart(2, '0')}`; // Форматируем время в HH:mm
    const timezone = timezoneSelect.value; // Получаем выбранный часовой пояс

    const combinedDate = moment.tz(`${dateString} ${timeString}`, 'YYYY-MM-DD HH:mm', timezone);
    
    return [combinedDate.unix(), combinedDate.toISOString()];
};


const combineTime = () => {
  const dateString = `${datePush.value.getFullYear()}-${(datePush.value.getMonth() + 1).toString().padStart(2, '0')}-${datePush.value.getDate().toString().padStart(2, '0')}`;
  const timeString = timePush.value;
  const timezone = timezoneSelect.value;

  const combinedDate = new Date(`${dateString} ${timeString}`);

  console.log('Текущее время: ', combineCurrentTime()[1]);
  console.log('Выбранное время: ', combinedDate.toISOString());
  console.log(`${dateString} ${timeString}`);
  
  if(combineCurrentTime()[0] > Math.floor(+combinedDate / 1000)){
    return {'status': 'fail', 'detail': 'Время не может быть меньше чем текущее.'}
  }
  const isoString = combinedDate.toISOString();

  return {'status': 'ok', 'detail': isoString, 'date': combinedDate};
}

const checkDetails = () => {
  if(telegramStore.selectedAccount === null){
    return {'status': 'fail', 'detail': 'Не выбран аккаунт!'};
  }
  if(namePush.value.length === 0){
    return {'status': 'fail', 'detail': 'Имя пуша не может быть пустым'};
  }
  if(timezoneSelect.value.length === 0){
    return {'status': 'fail', 'detail': 'Необходимо выбрать часовой пояс.'}
  }
  const time = combineTime();
  if(time.status === 'fail'){
    return time;
  }

  return {'status': 'ok', 'detail': {
    'date_push': time.detail,
    'datedate_push_not_utc_push': toIsoStringWithoutUtc(time.date)
  }}
}



// Проверка сообщения в избранном...
const checkPushMessage = async () => {
  const messageTypeSend = {
    'Текст': 'text',
    'Текст+Медиа': 'text_and_media',
    'Видео Сообщение': 'video_note',
    'Голосовое сообщение': 'voice_note'
  }[messageType.value];

  const formData = new FormData();

  if(messageTypeSend === 'text' || messageTypeSend === 'text_and_media'){
    if(sendTextData.value.length === 0 && filesData.value.length === 0){
      alert('Сообщение не может быть пустым.');
      return;
    } else {
      if(messageTypeSend === 'text'){
        formData.append('files_list', new File([], 'empty.txt', {
          type: 'text/plain'
        }));
      }
    }
  }

  if(messageTypeSend === 'text_and_media'){
    for(let i = 0; i < filesData.value.length; i++){
      if(i === 9) break;

      formData.append('files_list', filesData.value[i]);
    }
  }
  if(messageTypeSend === 'video_note'){
    console.log(fileDataVideoNote.value)
    formData.append('files_list', fileDataVideoNote.value);
  }
  if(messageTypeSend === 'voice_note'){
    formData.append('files_list', fileDataVoiceNote.value);
  }

  formData.append('type_message', messageTypeSend);
  formData.append('text_message', sendTextData.value);
  formData.append('is_use_proxy', isUseProxy.value);
  formData.append('proxy_data', selectedProxy.value);

  isLoadingPush.value = true;
  checkPushMessageFailData.value = '';
  try{


    const res = await axios.post(`${apiUrl}/api/v1/push/check_push_message`, formData, {
      params: {
        'user_id': telegramStore.selectedAccount
      }
    }
    );
    if(res.data.status === 'fail'){
      checkPushMessageFailData.value = res.data.detail;
    }
  } catch(e) {

  } finally {
    isLoadingPush.value = false
  }
};


const checkPushDbMessageNow = async () => {
  if(namePush.value.length === 0){
    alert('Имя пуша не может быть пустым');
    return;
  }

  const messageTypeSend = {
    'Текст': 'text',
    'Текст+Медиа': 'text_and_media',
    'Видео Сообщение': 'video_note',
    'Голосовое сообщение': 'voice_note'
  }[messageType.value];

  const formData = new FormData();



  if(messageTypeSend === 'text' || messageTypeSend === 'text_and_media'){
    if(sendTextData.value.length === 0 && filesData.value.length === 0){
      alert('Сообщение не может быть пустым.');
      return;
    } else {
      if(messageTypeSend === 'text'){
        formData.append('files_list', new File([], 'empty.txt', {
          type: 'text/plain'
        }));
      }
    }
  }

  if(messageTypeSend === 'text_and_media'){
    for(let i = 0; i < filesData.value.length; i++){
      if(i === 9) break;

      formData.append('files_list', filesData.value[i]);
    }
  }
  if(messageTypeSend === 'video_note'){
    console.log(fileDataVideoNote.value)
    formData.append('files_list', fileDataVideoNote.value);
  }
  if(messageTypeSend === 'voice_note'){
    formData.append('files_list', fileDataVoiceNote.value);
  }

  formData.append('type_db', bdType.value);
  formData.append('limit', maxParsingCount.value.toString());
  formData.append('type_message', messageTypeSend);
  formData.append('text_message', sendTextData.value);
  formData.append('push_name', namePush.value);
  formData.append('hours_limit', hoursLimit.value);
  formData.append('hours_limit_msg', hoursLimitBot.value);
  formData.append('timezone', timezoneSelect.value);
  formData.append('limit_speed', limitSpeedValue.value);

  formData.append('is_use_proxy', isUseProxy.value);
  formData.append('proxy_data', selectedProxy.value);

  isLoadingPush.value = true;
  checkPushMessageFailData.value = '';

  try{
    const res = await axios.post(`${apiUrl}/api/v1/push/send_push_messages_now`, formData, {
      params: {
        'user_id': telegramStore.selectedAccount
      }
    });

    if(res.data.status === 'fail'){
      checkPushMessageFailData.value = res.data.detail;
    }
  } catch(e) {

  } finally {
    isLoadingPush.value = false
  }
};

// Отправка пушей в базы данных (RD и FD)
const checkPushDbMessage = async () => {
  const details = checkDetails();

  if(details.status === 'fail'){
    alert(details.detail)
    return;
  }

  const messageTypeSend = {
    'Текст': 'text',
    'Текст+Медиа': 'text_and_media',
    'Видео Сообщение': 'video_note',
    'Голосовое сообщение': 'voice_note'
  }[messageType.value];

  const formData = new FormData();



  if(messageTypeSend === 'text' || messageTypeSend === 'text_and_media'){
    if(sendTextData.value.length === 0 && filesData.value.length === 0){
      alert('Сообщение не может быть пустым.');
      return;
    } else {
      if(messageTypeSend === 'text'){
        formData.append('files_list', new File([], 'empty.txt', {
          type: 'text/plain'
        }));
      }
    }
  }

  if(messageTypeSend === 'text_and_media'){
    for(let i = 0; i < filesData.value.length; i++){
      if(i === 9) break;

      formData.append('files_list', filesData.value[i]);
    }
  }
  if(messageTypeSend === 'video_note'){
    console.log(fileDataVideoNote.value)
    formData.append('files_list', fileDataVideoNote.value);
  }
  if(messageTypeSend === 'voice_note'){
    formData.append('files_list', fileDataVoiceNote.value);
  }

  formData.append('type_db', bdType.value);
  formData.append('limit', maxParsingCount.value.toString());
  formData.append('type_message', messageTypeSend);
  formData.append('text_message', sendTextData.value);
  formData.append('is_use_proxy', isUseProxy.value);
  formData.append('proxy_data', selectedProxy.value);

  formData.append('push_name', namePush.value);
  formData.append('date_push', details.detail.date_push);
  formData.append('date_push_not_utc', details.detail.datedate_push_not_utc_push);
  formData.append('timezone', timezoneSelect.value);
  formData.append('hours_limit', hoursLimit.value);
  formData.append('hours_limit_msg', hoursLimitBot.value);
  formData.append('limit_speed', limitSpeedValue.value);

  isLoadingPush.value = true;
  checkPushMessageFailData.value = '';

  try{
    const res = await axios.post(`${apiUrl}/api/v1/push/send_push_messages`, formData, {
      params: {
        'user_id': telegramStore.selectedAccount
      }
    });

    if(res.data.status === 'fail'){
      checkPushMessageFailData.value = res.data.detail;
    } else {
      bdType.value = null;
    }
  } catch(e) {

  } finally {
    isLoadingPush.value = false
  }
};


const bdType = ref(null);
const messageType = ref('Текст');
const filesData = ref([]);
const fileDataVideoNote = ref([]);
const fileDataVoiceNote = ref([]);

const maxParsingCount = ref(0);
const hoursLimit = ref(0);
const hoursLimitBot = ref(0);

const error = ref(null);

const sendTextData = ref('');

// Проверка текста сообщения на длину
const checkTextDataSize = () => {
  if(sendTextData.value.length >= 4096){
    sendTextData.value = sendTextData.value.slice(0, 4096);
    error.value = 'Размер текста больше 4096 символов!';
  } else {
    error.value = null;
  }
}

const handleAllFilesUpload = (event) => {
  console.log(event);
  filesData.value = event.slice(0, 9);
  event = event.slice(0, 9);
}

const handleVideoUpload = (event) => {
  let file = undefined;

  if(Array.isArray(event)){
    file = event.target.files[0];
  } else {
    file = event;
  }

  if (file) {
      error.value = null;

      const maxFileSize = 15 * 1024 * 1024;
      if (file.size > maxFileSize) {
        error.value = `Размер видео не должен превышать 15MB. Текущий размер: ${(file.size / (1024 * 1024)).toFixed(2)} MB.`;
        return;
      }

      const videoUrl = URL.createObjectURL(file);
      const videoElement = document.createElement('video');

      videoElement.onloadedmetadata = () => {
        const videoDuration = videoElement.duration;
        const videoWidth = videoElement.videoWidth;
        const videoHeight = videoElement.videoHeight;

        if (videoWidth !== videoHeight) {
          error.value = `Соотношение сторон видео должно быть 1:1. Текущее соотношение: ${videoWidth}:${videoHeight}.`;
          return;
        }

        if (videoDuration > 60) {
          error.value = `Длительность видео не должна превышать 1 минуту. Текущая длительность: ${Math.floor(videoDuration)} секунд.`;
          return;
        }

        error.value = null;
      };

      videoElement.src = videoUrl;
  }
};


onMounted(async () => {
  await proxiesStore.fetchProxies();
  await telegramStore.getAccountsList();

  window.onbeforeunload = () => {
    if(['', 'need create session', 'account is not active'].indexOf(telegramStore.detailsError) === -1)
        return telegramStore.detailsError;
  }
});

</script>


<template>

  <v-sheet
    class="pa-6 text-white mx-auto"
    width="100%"
    rounded
  >
  <div>
    <h4 class="text-h5 font-weight-bold mb-4">Настройки рассылки</h4>
    <v-divider></v-divider>
  </div>
  <div v-if="telegramStore.isLoading">
      <div class="mt-2">
          <v-progress-circular :size="50" indeterminate></v-progress-circular>
      </div>
  </div>
  <div v-else>
    <div class="mt-4">
      <v-select
      label="Аккаунт для рассылки"
      :items="telegramStore.accountsList.map(i => i.account_id)"
      v-model="telegramStore.selectedAccount"
      v-on:update:model-value="telegramStore.getAccInfo"
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


    <div v-if="telegramStore.selectedAccount === null">
      <v-alert text="Для просмотра выберите аккаунт." type='info'></v-alert>
    </div>
    <div v-if="telegramStore.accountData !== null">
      <v-divider></v-divider>
      <div class="mt-2">
        <v-radio-group label="База для рассылки" v-model="bdType">
          <v-radio label="FD база" value="fd"></v-radio>
          <v-radio label="RD база" value="rd"></v-radio>
          <v-radio label="RD база (Закреп)" value="rd_pinned"></v-radio>
        </v-radio-group>
        <v-select
          label="Тип сообщения"
          :items="['Текст', 'Текст+Медиа', 'Видео Сообщение', 'Голосовое сообщение']"
          v-model="messageType"
          variant="outlined"
        ></v-select>
      </div>
  
  
      <v-divider></v-divider>
  
      <div class="mt-4">
        <div v-if="messageType === 'Текст'">
          <v-textarea @update:model-value="checkTextDataSize" v-model="sendTextData" label="Текст сообщения" variant="outlined"></v-textarea>
        </div>
        <div v-if="messageType === 'Текст+Медиа'">
          <v-alert text="Поддерживаются только файлы с расширением .jpg, .png, .mp4! Максимальное количество файлов 9 штук." type="info" variant="outlined" class="mb-4"></v-alert>
          <v-file-input @update:model-value="handleAllFilesUpload" v-model="filesData" multiple counter show-size class="mb-2" label="Медиа файлы" variant="outlined" accept="image/png, image/jpeg, video/mp4"></v-file-input>
          <v-textarea  @update:model-value="checkTextDataSize" v-model="sendTextData" label="Текст сообщения" variant="outlined"></v-textarea>
        </div>
        <div v-if="messageType === 'Видео Сообщение'">
          <v-alert text="Поддерживаются тольк файл с расширением .mp4! Максимальное количество файлов 1 штука." type="info" variant="outlined" class="mb-4"></v-alert>
          <v-file-input @update:model-value="handleVideoUpload" v-model="fileDataVideoNote" label="Медиа файл" variant="outlined" accept="video/mp4"></v-file-input>
        </div>
        <div v-if="messageType === 'Голосовое сообщение'">
          <v-alert text="Поддерживаются тольк файл с расширением .ogg, .mp3! Максимальное количество файлов 1 штука." type="info" variant="outlined" class="mb-4"></v-alert>
          <v-file-input label="Медиа файл" variant="outlined" v-model="fileDataVoiceNote" accept="audio/ogg, audio/mpeg"></v-file-input>
        </div>
  
        <div v-if="error">
          <v-alert :text="error" type="error" variant="outlined"></v-alert>
        </div>
        <div>
          Лимит пользователей
          <v-text-field variant="outlined" type='number' v-model="maxParsingCount" class="ma-2" density="compact" placeholder="Лимит" hide-details></v-text-field>
        </div>
        <div>
          Лимит по времени на последний пуш (в часах)
          <v-text-field variant="outlined" type='number' v-model="hoursLimit" class="ma-2" density="compact" placeholder="Лимит времени (в часах)" hide-details></v-text-field>
        </div>
        <div>
          Лимит по времени на последнее сообщение (в часах)
          <v-text-field variant="outlined" type='number' v-model="hoursLimitBot" class="ma-2" density="compact" placeholder="Лимит времени (в часах)" hide-details></v-text-field>
        </div>
        <div class="mt-5">
          <v-select
            label="Лимит по скорости"
            :items="[
              'Без ограничений',
              'Минимальная',
              'Средняя',
              'Медленная'
            ]"
            v-model="limitSpeed"
            v-on:update:model-value="onLimitSpeedupdate"
            variant="outlined"
          ></v-select> 
        </div>
  
      </div>
  
      <!-- <v-divider></v-divider> -->
  
      <div>
        <v-text-field variant="outlined" placeholder="Название пуша" v-model="namePush"></v-text-field>
        <v-autocomplete
          label="Часовой пояс"
          :items="timezoneList"
          v-model="timezoneSelect"
          variant="outlined"
        ></v-autocomplete> 
        <v-date-input :model-value="datePush" v-on:update:model-value="validateDateTime" label="Дата" variant="outlined"></v-date-input>
  
          <v-text-field
            v-model="timePush"
            :active="menu2"
            :focus="menu2"
            label="Время"
            :prepend-icon="mdiClockTimeFourOutline"
             variant="outlined"
            readonly
          >
            <v-menu
              v-model="menu2"
              :close-on-content-click="false"
              activator="parent"
              transition="scale-transition"
            >
              <v-time-picker
                v-if="menu2"
                v-model="timePush"
                full-width
                format='24hr'
              ></v-time-picker>
            </v-menu>
          </v-text-field>

          <v-checkbox v-model="isUseProxy" label="Использовать прокси"></v-checkbox>
          <v-autocomplete
            v-if="isUseProxy"
            label="Прокси"
            :items="proxiesStore.formattedProxies()"
            v-model="selectedProxy"
            item-title="display"
            variant="outlined"
          ></v-autocomplete> 
          
      </div>
      <div class="d-flex flex-wrap">
        <div class="mr-2">
          <v-btn color="green" class="mt-2" @click.native="checkPushDbMessage" :loading="isLoadingPush" :disabled="error !== null || bdType === null" variant="tonal">
            Добавить пуш в список
          </v-btn>
        </div>
        <div class="mr-2">
          <v-btn color="blue" class="mt-2" @click.native="checkPushDbMessageNow" :loading="isLoadingPush" :disabled="error !== null || bdType === null" variant="tonal">
            Отправить сейчас
          </v-btn>
        </div>
        <div>
          <v-btn variant="tonal" class="mt-2" @click.native="checkPushMessage" :loading="isLoadingPush" :disabled="error !== null">
            Проверить сообщение
          </v-btn>
        </div>
      </div>
      <div class="mt-4" v-if="checkPushMessageFailData.length > 0">
        <v-alert :text="checkPushMessageFailData" type="error" variant="outlined"></v-alert>
      </div>
    </div>
  </div>
  </v-sheet>

  <v-sheet
    class="pa-6 text-white mx-auto mt-4"
    width="100%"
    rounded
  >
  <h1 class="mb-4">Логи</h1>
  <v-divider></v-divider>

  <v-textarea v-model="logsTelethonProgram" clearable readonly label="Логи работы" variant="outlined"></v-textarea>

  </v-sheet>

</template>
