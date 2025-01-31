import axios from 'axios';

export function isTokenExpired(token){
    if(!token) return true;

    const decodedToken = jwtDecode(token);
    const currentTime = Date.now() / 1000;

    return decodedToken.exp < currentTime;
}


export function jwtInterceptor(){
    axios.interceptors.request.use(request => {
        const userData = JSON.parse(localStorage.getItem('user'));
        const token = userData?.token;

        const isLoggedIn = !!token;

        const isApiUrl = import.meta.env.VITE_APIURL;
        if(isLoggedIn && isApiUrl){
            request.headers.Authorization = `Bearer ${token}`;
        }

        return request;
    });
}