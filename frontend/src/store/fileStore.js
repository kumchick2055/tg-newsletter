import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useFileStore = defineStore('fileStore', () => {
  const bdType = ref('fd');
  const messageType = ref('Текст');
  const filesData = ref([]);
  const error = ref(null);
  const sendTextData = ref('');

  const checkTextDataSize = () => {
    if (sendTextData.value.length >= 4096) {
      sendTextData.value = sendTextData.value.slice(0, 4096);
      error.value = 'Размер текста больше 4096 символов!';
    } else {
      error.value = null;
    }
  };


  const handleAllFilesUpload = (event) => {
    console.log(event);
    filesData.value = event.slice(0, 9);
  };


  const handleVideoUpload = (event) => {
    let file = undefined;

    if (Array.isArray(event)) {
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

  return {
    bdType,
    messageType,
    filesData,
    error,
    sendTextData,
    checkTextDataSize,
    handleAllFilesUpload,
    handleVideoUpload,
  };
});