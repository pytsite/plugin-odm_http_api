import httpApi from '@pytsite/http-api';

function getEntities(model, args) {
    return httpApi.get(`odm/entities/${model}`, args);
}

function getEntity(ref, args) {
    return httpApi.get(`odm/entity/${ref}`, args);
}

function postEntity(model, data) {
    return httpApi.post(`odm/entity/${model}`, data);
}

function patchEntity(ref, data) {
    return httpApi.patch(`odm/entity/${ref}`, data);
}

function deleteEntity(ref, args) {
    return httpApi.del(`odm/entity/${ref}`, args);
}

const api = {
    getEntities: getEntities,
    getEntity: getEntity,
    postEntity: postEntity,
    patchEntity: patchEntity,
    deleteEntity: deleteEntity
};

export default api;
