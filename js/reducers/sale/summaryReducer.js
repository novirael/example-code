const initialState = {
    data: {
        invoices: []
    },
    fetched: false,
    error: null
};

export default function reducer(state=initialState, action) {

    switch (action.type) {
        case "FETCH_SALE_SUMMARY_REJECTED": {
            return { ...state, fetching: false, error: action.payload.detail }
        }
        case "FETCH_SALE_SUMMARY_FULFILLED": {
            return {
                ...state,
                fetched: true,
                data: action.payload
            }
        }
    }

    return state
}
