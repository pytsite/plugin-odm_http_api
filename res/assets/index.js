import httpApi from '@pytsite/http-api';

function _parseLinkHeader(headerStr) {
    const r = {};

    headerStr.split(',').map(link => {
        const match = link.match(/<(.+?)>; rel="(.+?)"/);
        if (match)
            r[match[2]] = match[1];
    });

    return r;
}

async function getEntities(model, args) {
    return httpApi.get(`odm/entities/${model}`, args);
}

async function getAllEntities(model, args) {
    let r = [];
    let url = httpApi.url(`odm/entities/${model}`, args);

    while (url) {
        const resp = await httpApi.get(url, null, true);
        r = r.concat(resp.data);
        url = _parseLinkHeader(resp.response.getResponseHeader('Link')).next;
    }

    return r;
}

async function getEntity(ref, args) {
    return httpApi.get(`odm/entity/${ref}`, args);
}

async function postEntity(model, data) {
    return httpApi.post(`odm/entity/${model}`, data);
}

async function patchEntity(ref, data) {
    return httpApi.patch(`odm/entity/${ref}`, data);
}

async function deleteEntity(ref, args) {
    return httpApi.del(`odm/entity/${ref}`, args);
}

const api = {
    getEntities: getEntities,
    getAllEntities: getAllEntities,
    getEntity: getEntity,
    postEntity: postEntity,
    patchEntity: patchEntity,
    deleteEntity: deleteEntity
};

export default api;
