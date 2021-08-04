import React, { useState } from "react";
import { Navbar, Nav, Modal, Button, Form } from "react-bootstrap";
import styled from "styled-components";
import { useInput } from "sagemaker-worker";
import Utils from "utils";
import { useStoreState } from "appstore";
const LogoImage = styled.img`
  height: 24px;
  margin-right: 1.5rem;
`;

const InstructionsModal = (props: {
  show: boolean;
  handleClose: () => void;
}) => {
  const { show, handleClose } = props;
  return (
    <Modal show={show} onHide={handleClose}>
      <Modal.Header closeButton>
        <Modal.Title>Instructions</Modal.Title>
      </Modal.Header>

      <Modal.Body>
        <p>Tabular Document Digitization annotator instructions here</p>
      </Modal.Body>

      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

const RejectModal = (props: { show: boolean; handleClose: () => void }) => {
  const { show, handleClose } = props;
  const [reason, setReason] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const documentModel = useStoreState((s) => s.documentModel);
  const [reasonRequiredError, setReasonRequiredError] = useState("");
  const reject = async () => {
    if (!reason) {
      setReasonRequiredError("A reason is required");
      return;
    }
    setIsSubmitting(true);
    await Utils.submitReject(documentModel, reason);
    setIsSubmitting(false);
    handleClose();
  };
  return (
    <Modal show={show} onHide={handleClose}>
      <Modal.Header closeButton>
        <Modal.Title>Reject Document?</Modal.Title>
      </Modal.Header>

      <Modal.Body>
        <Form>
          <Form.Group controlId="exampleForm.ControlTextarea1">
            <Form.Label>What is wrong with this document?</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              isInvalid={reasonRequiredError !== ""}
            />
            <Form.Control.Feedback type="invalid">
              {reasonRequiredError}
            </Form.Control.Feedback>
          </Form.Group>
        </Form>
      </Modal.Body>

      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>
          Cancel
        </Button>
        <Button variant="danger" onClick={reject} disabled={isSubmitting}>
          Reject Document
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

const SubmitConfirmModal = (props: {
  show: boolean;
  handleClose: () => void;
}) => {
  const { show, handleClose } = props;
  const [isSubmitting, setIsSubmitting] = useState(false);
  const documentModel = useStoreState((s) => s.documentModel);
  const submit = async () => {
    setIsSubmitting(true);
    await Utils.submit(documentModel);
    setIsSubmitting(false);
    handleClose();
  };
  return (
    <Modal show={show} onHide={handleClose}>
      <Modal.Header closeButton>
        <Modal.Title>Submit Document?</Modal.Title>
      </Modal.Header>

      <Modal.Body>
        <p>Are you sure you want to submit this document?</p>
      </Modal.Body>

      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>
          Cancel
        </Button>
        <Button variant="primary" onClick={submit} disabled={isSubmitting}>
          Submit Document
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default () => {
  const [showInstructions, setShowInstructions] = useState(false);
  const [showReject, setShowReject] = useState(false);
  const [showSubmit, setShowSubmit] = useState(false);
  const logoUrl = useInput("logo");
  const hideInstructionsModal = () => {
    setShowInstructions(false);
  };
  const showInstructionsModal = (e: React.MouseEvent) => {
    e.preventDefault();
    setShowInstructions(true);
  };
  const toggleRejectModal = () => {
    setShowReject(!showReject);
  };
  const toggleSubmitModal = () => {
    setShowSubmit(!showSubmit);
  };
  return (
    <Navbar bg="dark" variant="dark" expand="lg">
      <Navbar.Brand className="d-flex align-items-center mr" href="#home">
        <LogoImage src={logoUrl} /> Tabular Document Annotation Tool
      </Navbar.Brand>
      <Navbar.Toggle aria-controls="basic-navbar-nav" />
      <Navbar.Collapse id="basic-navbar-nav">
        <Nav className="mr-auto">
          <Nav.Link href="" onClick={showInstructionsModal}>
            Instructions
          </Nav.Link>
          <InstructionsModal
            show={showInstructions}
            handleClose={hideInstructionsModal}
          />
        </Nav>
      </Navbar.Collapse>
      <div>
        <Button variant="danger" className="mr-2" onClick={toggleRejectModal}>
          Reject
        </Button>
        <RejectModal show={showReject} handleClose={toggleRejectModal} />
        <Button variant="success" onClick={toggleSubmitModal}>
          Submit
        </Button>
        <SubmitConfirmModal show={showSubmit} handleClose={toggleSubmitModal} />
      </div>
    </Navbar>
  );
};
