<script setup>
  import { useTgStore } from "@/store/tgStore";
  import { mdiAlert } from "@mdi/js";
  import {onMounted, ref} from "vue";
  
    

  const telegramStore = useTgStore();


  // Диалоговое окно для выхода из аккаунта
  const exitFromAccount = ref(false);

  // Выход из аккаунта
  const exitFromAcc = async () => {
    const res = await telegramStore.exitTgSession();
    if(res){
      exitFromAccount.value = false;
    }
  }

  onMounted(async () => {
    await telegramStore.getAccountsList();
  })

  document.title = "Менеджер TG Аккаунтов";
</script>


<template>
    <v-sheet
    class="pa-6 text-white mx-auto mb-4"
    width="100%"
    rounded
  >
  <div>
    <h4 class="text-h5 font-weight-bold mb-4">Менеджер TG Аккаунтов</h4>
    <v-divider></v-divider>
  </div>

  

  <div v-if="telegramStore.isLoading" class="mt-4">
    <v-progress-circular :size="50" indeterminate></v-progress-circular>
  </div> 
  <div class="mt-4" v-else>
    <div class="text-h6 mb-2">Выбрать аккаунт</div>
   <v-select
      label="Select"
      :items="telegramStore.accountsList.map(i => i.account_id)"
      v-model="telegramStore.selectedAccount"
      v-on:update:model-value="telegramStore.getAccInfo"
      variant="outlined"
    ></v-select> 

    <div v-if="telegramStore.selectedAccount">
      <div class="mb-2">
        Информация:
      </div>
      <div>
        <v-divider></v-divider>
      </div>
      <div class="mt-2 mb-4" v-if="telegramStore.accountData !== null">
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
      <div v-else class="mb-2 mb-4">
        Аккаунт не доступен.
      </div>
      <div class="mb-2">
        Действия:
      </div>
      <div>
        <v-divider></v-divider>
      </div>
      <div>
        <v-btn @click.native="exitFromAccount = true" variant="tonal" class="mt-4">Выйти из аккаунта</v-btn>
      </div>
    </div>
  </div>

  </v-sheet>

  <!-- Диалоговое окно для выхода из аккаунта... -->
  <v-dialog
      v-model="exitFromAccount"
      width="auto"
    >
      <v-card
        max-width="400"
        :prepend-icon="mdiAlert"
        text="Выйти из аккаунта?"
        title="Предупреждение"
      >
        <template v-slot:actions>
          <v-btn
            text="Да"
            :loading="telegramStore.isLoading"
            @click.native="exitFromAcc"
          ></v-btn>
          <v-btn
            text="Нет"
            :loading="telegramStore.isLoading"
            @click="exitFromAccount = false"
          ></v-btn>
        </template>
      </v-card>
  </v-dialog>

  <v-sheet
            class="pa-6 text-white mx-auto mb-4"
            width="100%"
            rounded
          >
          <h4 class="mb-4 text-h5 font-weight-bold ">Добавление аккаунта</h4>

          <v-divider></v-divider>
          
          <div v-if="telegramStore.isLoading">
            <div class="mt-2">
                <v-progress-circular :size="50" indeterminate></v-progress-circular>
            </div>
          </div>
          <div v-else>
            <div>
              <!-- Создание новой сессии -->
              <div v-if="telegramStore.detailsError === ''">
                <v-text-field variant="outlined" v-model="telegramStore.apiId" class="mt-4" label="API Id"></v-text-field>
                <v-text-field variant="outlined" v-model="telegramStore.apiHash" label="API Hash"></v-text-field>

                <v-btn
                  variant="tonal"
                  @click.native="telegramStore.createTgSession"
                  :loading="telegramStore.isLoadingAuth"
                  :disabled="telegramStore.apiId.length === 0 || telegramStore.apiHash.length === 0"
                  >
                    Продолжить
                </v-btn>


                <v-alert
                v-if="telegramStore.detailsError === 'failed to create session'"
                text="Не удалось создать сессию"
                type="error"
                class="mb-4 mt-2"
                variant="outlined"
                ></v-alert>
              </div>

              <!-- Номер Телефона -->
              <div v-if="telegramStore.detailsError === 'input phone' || telegramStore.detailsError === 'failed to input phone'">
                <v-text-field variant="outlined" v-model="telegramStore.phone" class="mt-4" label="Номер Телефона"></v-text-field>

                <v-btn
                  variant="tonal"
                  @click.native="telegramStore.sendPhoneData"
                  :loading="telegramStore.isLoadingAuth"
                  :disabled="telegramStore.apiId.length === 0 || telegramStore.apiHash.length === 0"
                  >
                    Продолжить
                </v-btn>


                <v-alert
                v-if="telegramStore.detailsError === 'failed to input phone'"
                text="Неверный номер телефона"
                type="error"
                class="mb-4 mt-2"
                variant="outlined"
                ></v-alert>
              </div>

              <!-- Код из смс -->
              <div v-if="telegramStore.detailsError === 'need code' || telegramStore.detailsError === 'failed to input code'">
                <v-text-field  variant="outlined"v-model="telegramStore.smsCode" class="mt-4" label="Смс Код"></v-text-field>

                <v-btn
                  variant="tonal"
                  @click.native="telegramStore.sendSmsCode"
                  :loading="telegramStore.isLoadingAuth"
                  :disabled="telegramStore.apiId.length === 0 || telegramStore.apiHash.length === 0"
                  >
                    Продолжить
                </v-btn>


                <v-alert
                v-if="telegramStore.detailsError === 'failed to input code'"
                text="Неверный смс код"
                type="error"
                class="mb-4 mt-2"
                variant="outlined"
                ></v-alert>
              </div>

              <div v-if="telegramStore.detailsError === 'need password' || telegramStore.detailsError === 'failed to input password'">
                <v-text-field variant="outlined" v-model="telegramStore.password" class="mt-4" label="Пароль"></v-text-field>

                <v-btn
                  variant="tonal"
                  @click.native="telegramStore.sendPasswordData"
                  :loading="telegramStore.isLoadingAuth"
                  :disabled="telegramStore.apiId.length === 0 || telegramStore.apiHash.length === 0"
                  >
                    Продолжить
                </v-btn>


                <v-alert
                v-if="telegramStore.detailsError === 'failed to input password'"
                text="Неверный пароль"
                type="error"
                class="mb-4 mt-2"
                variant="outlined"
                ></v-alert>
              </div>

              <div v-if="telegramStore.detailsError === 'account is not active'">
                <v-alert
                  text="Аккаунт не активен, требуется перезайти в него!"
                  type="error"
                  class="mb-4 mt-2"
                  variant="outlined"
                  ></v-alert>
              </div>
                <v-alert
                  v-if="telegramStore.fullDetailError"
                  :text="telegramStore.fullDetailError"
                  type="error"
                  class="mb-4 mt-2"
                  variant="outlined"
                  ></v-alert>

            </div>


          </div>



  </v-sheet>
</template>
