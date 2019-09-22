import { browserHistory } from 'react-router';

import Requests from '../utils/requests';


export function fetchCategories() {
    return function(dispatch) {
        Requests.loadData(
            '/api/sale/v1/categories/',
            response => {
                dispatch(
                    {type: "FETCH_SALE_CATEGORY_LIST_FULFILLED", payload: response}
                );
            },
            err => dispatch(
                {type: "FETCH_SALE_CATEGORY_LIST_REJECTED", payload: err}
            )
        );
    }
}

export function fetchInvoice(invoiceId) {
    return function(dispatch) {
        Requests.loadData(
            `/api/sale/v1/invoices/${invoiceId}/`,
            data => {
                dispatch(
                    {type: "FETCH_SALE_INVOICE_FULFILLED", payload: data}
                );
                let contractorRequests = [];
                if (data.customerId) {
                    contractorRequests.push(
                        dispatch(fetchInvoiceContractor(data.customerId,  'customer'))
                    );
                }
                if (data.receiverId) {
                    contractorRequests.push(
                        dispatch(fetchInvoiceContractor(data.receiverId, 'receiver'))
                    );
                }
                Promise.all(contractorRequests).then(data => {
                    console.log(data)
                    dispatch(
                        {type: "FETCH_SALE_INVOICE_COMPLETED"}
                    )
                });
            },
            err => dispatch(
                {type: "FETCH_SALE_INVOICE_REJECTED", payload: err}
            )
        );
    }
}

function fetchInvoiceContractor(contractorId, contractorKey = 'contractor') {
    return function(dispatch) {
        console.log('fetchInvoiceContractor', contractorId);
        return Requests.loadData(
            `/api/business/v1/contractors/${contractorId}/`,
            response => dispatch({
                type: "FETCH_SALE_INVOICE_CONTRACTOR_FULFILLED",
                payload: {
                    data: response,
                    key: contractorKey,
                },
            }),
            err => dispatch({
                type: "FETCH_SALE_INVOICE_CONTRACTOR_REJECTED",
                payload: err,
            }),
        );
    }
}

export function fetchInvoices(queries) {
    let basePath = '/api/sale/v1/invoices/?is_draft=false',
        path = queries ? basePath + queries.join("&") : basePath;

    return function(dispatch) {
        Requests.loadData(
            path,
            response => {
                dispatch(
                    {type: "FETCH_SALE_INVOICE_LIST_FULFILLED", payload: response}
                );
            },
            err => dispatch(
                {type: "FETCH_SALE_INVOICE_LIST_REJECTED", payload: err}
            )
        );
    }
}


export function fetchSummary(queries) {
    let basePath = '/api/sale/v1/summary/',
        path = queries ? basePath + '?' + queries.join("&") : basePath;

    return function(dispatch) {
        Requests.loadData(
            path,
            response => dispatch(
                {type: "FETCH_SALE_SUMMARY_FULFILLED", payload: response}
            ),
            err => dispatch(
                {type: "FETCH_SALE_SUMMARY_REJECTED", payload: err}
            )
        );
    }
}