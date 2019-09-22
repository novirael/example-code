const initialState = {
    data: {
        id: 0,
        unique_number: '',
        items: [],
    },
    fetched: false,
};

export default function reducer(state=initialState, action) {

    switch (action.type) {
        case "FETCH_SALE_INVOICE_REJECTED": {
            return { ...state, fetching: false, error: action.payload.detail }
        }
        case "FETCH_SALE_INVOICE_FULFILLED": {
            return {
                ...state,
                data: {
                    ...state.data,
                    ...action.payload,
                },
            };
        }
        case "FETCH_SALE_INVOICE_CONTRACTOR_FULFILLED": {
            return {
                ...state,
                data: {
                    ...state.data,
                    [action.payload.key]: {
                        ...action.payload.data,
                    },
                },
            }
        }
        case "FETCH_SALE_INVOICE_COMPLETED": {
            return {
                ...state,
                fetched: true,
            }
        }
    }

    return state;
}
