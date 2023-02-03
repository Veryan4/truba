import { userService } from "../services";

export function authGuard() {
    const user = userService.getUser();
    if (user) {
        return new Promise(()=> true).then(() => true)
    }
    return userService.me().then((user) => {
        if (user) {
            return true;
        } else {
            throw new Error('User not logged in');
        }
    }).catch(() => 'login');
}