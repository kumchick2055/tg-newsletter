import { defineStore } from "pinia";
import axios from "axios";

const apiUrl = import.meta.env.VITE_APIURL;

export const useAuthStore = defineStore('auth', {
    state: () => ({
        login: '',
        password: '',
        isLoading: false
    }),
    actions: {
        async authorization(){
            this.isLoading = true;

            try{

                const res = await axios.post(`${apiUrl}/api/v1/auth/login`, {
                    login: this.login,
                    password: this.password
                });

                return res.data;
            } catch(e) {
                return {'error': true, 'data': e}
            } finally {
                this.isLoading = false;
            }
            
            
            return {'error': false}
        },
        logout(){
            try{
                localStorage.removeItem('user');
            } catch(e){
                return false;
            }

            return true;
        }
    }
});