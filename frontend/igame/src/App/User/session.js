/**
 * use to handle session
 * localstorage is a html5 local storage solution
 * set_sid(sid) set sid into localstorage
 * get_sid()    get sid from the local or return false if no.
 * destroy()    remove sid from localstorage
 */
const session = {
    sid: null,
    set_sid: function (sid) {
        localStorage.sid = sid;
        this.sid = sid;
    },
    get_sid: function () {
        if (localStorage && localStorage.sid) {
            return localStorage.sid;
        } else {
            return false;
        }
    },
    destroy: function(){
        if (localStorage && localStorage.sid) localStorage.removeItem('sid');
    }
};

export default session;