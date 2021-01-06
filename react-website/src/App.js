import React from 'react';
import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import './App.css'


function App() {
  return (
    <div style={{"margin": "auto", "width": "100%", "height": "100vh"}}>
    <Button>Test Button</Button>

    <h1> Testing some text</h1>
    <hr/>

    <h3> Testing some more text. The quick brown fox</h3>
    <hr/>
    <p>Jumps over the lazy dog. So lazy</p>

    <hr/>
    <span>This is the <i>final</i> <b>test</b> text.</span>
    <HeaderBox></HeaderBox>
    </div>
  );
}


class HeaderBox extends React.Component {

  render() {

    return <Container fluid className="h-50">
      <Row className="h-100 m-0 p-0 header-background">
        <Col></Col>
        <Col xs={8} className="my-auto header-box"> Build with Luca.</Col>
        <Col></Col>      
      </Row>
    </Container>;
  }
}

export default App;
