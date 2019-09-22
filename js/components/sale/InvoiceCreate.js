import React from 'react';
import { Grid } from 'react-bootstrap';
import Header from '../Header';
import LinksBar from '../LinksBar';

import InvoiceForm from './InvoiceFormContainer';

function InvoiceCreate({createInvoice, dataFetched}) {
    if (!dataFetched) {
        return null;
    }

    return (
        <Grid>
            <Header
                title="Faktury"
                subtitle="utwórz nowy dokument"
            />
            <LinksBar
                breadcrumbs={[
                    { label: 'Faktury', ref: '/sale/invoices/' },
                    { label: 'Utwórz', ref: null },
                ]}
            />
            <InvoiceForm
                onSubmit={createInvoice}
            />
        </Grid>
    )
};

export default InvoiceCreate;
