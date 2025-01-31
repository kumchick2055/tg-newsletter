import { defineStore } from 'pinia';
import axios from 'axios';


const apiUrl = import.meta.env.VITE_APIURL;


// Pinia Store Definition
export const useProxiesStore = defineStore('proxies', {
    state: () => ({
      proxyList: [],
      loading: false,
      error: null,
      loadingCheck: false,
      editingProxy: null,
    }),
    actions: {
      async fetchProxies() {
        this.loading = true;
        try {
          const response = await axios.get(`${apiUrl}/api/v1/proxies`);
          this.proxyList = response.data;
        } catch (error) {
          this.error = 'Ошибка загрузки списка прокси';
        } finally {
          this.loading = false;
        }
      },
  
      async addProxy(proxy) {
        this.loading = true;
        try {
          await axios.post(`${apiUrl}/api/v1/proxies`, {}, {params: proxy});
          await this.fetchProxies();
        } catch (error) {
          this.error = 'Ошибка добавления прокси';
        } finally {
          this.loading = false;
        }
      },
  
      async editProxy(proxy) {
        this.loading = true;
        try {
          await axios.put(`${apiUrl}/api/v1/proxies/${proxy.id}`, {},{params: proxy});
          await this.fetchProxies();
        } catch (error) {
          this.error = 'Ошибка редактирования прокси';
        } finally {
          this.loading = false;
        }
      },
  
      async deleteProxy(proxyId) {
        this.loading = true;
        try {
          await axios.delete(`${apiUrl}/api/v1/proxies/${proxyId}`);
          await this.fetchProxies();
        } catch (error) {
          this.error = 'Ошибка удаления прокси';
        } finally {
          this.loading = false;
        }
      },
  
      async checkProxy(proxyId) {
        this.loadingCheck = true;
        try {
          const response = await axios.post(`${apiUrl}/api/v1/proxies/${proxyId}/check`);
          if(response.data?.status === "valid"){
            alert("Валидные");
          } else {
            alert("Не валидные");
          }
          return response.data.status;
        } catch (error) {
            alert("Не валидные");
          this.error = 'Ошибка проверки прокси';
        } finally {
          this.loadingCheck = false;
        }
      },

      formattedProxies() {
        return this.proxyList.map(proxy => {
          let displayText =`socks5://${proxy.address}:${proxy.port}`;
          if(proxy.username !== "" && proxy.password !== ""){
            displayText = `socks5://${proxy.username}:${proxy.password}@${proxy.address}:${proxy.port}`
          }
          return {
            ...proxy,
            display: displayText
          };
        });
      }
    },
  });