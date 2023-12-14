import { useState } from 'react'
import './App.css'

import { Send as IconSend , MenuBook as IconBook} from "@mui/icons-material"

import { TextField,Grid,IconButton, Stack, Box, styled,Paper,Typography,Avatar, Skeleton} from "@mui/material"

import axios from "axios"

const api ="http://127.0.0.1:5000/assistant?input=";

  

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [lazy, setLazy] = useState(false);
  
  const handleClick = (message) => {
    if (input.trim() === "") return;
    setInput("");
    setLazy(true);
    setMessages((prevState) => [
      ...prevState,
      { sender: "human", message: message },
    ]);
    axios
      .get(api + message)
      .then((res) => {
        setMessages((prevState) => [
          ...prevState,
          { sender: "bot", message: res.data },
        ]);
      })
      .catch((ex) => {
        setMessages((prevState) => [
          ...prevState,
          {
            sender: "bot",
            message:
              "I'm sorry, we encountered an issue communicating with the API. Please try again later.",
          },
        ]);
        console.log(ex);
      })
      .finally(() => {
        setLazy(false);
      });
  };
  const handleKeyDown = (event) => {
    if (!event.shiftKey && event.key === "Enter") {
      handleClick(input);
    }
  };

  const HumanStyledPaper = styled(Paper)(({ theme }) => ({
    backgroundColor: theme.palette.mode === "dark" ? "#1A2027" : "#fff",
    ...theme.typography.body2,
    padding: theme.spacing(2),
    width: 800,
    color: theme.palette.text.primary,
    borderBottomLeftRadius: "0px",
    borderBottomRightRadius: "24px",
    borderTopRightRadius: "24px",
    borderTopLeftRadius: "24px",
  }));

  const BotStyledPaper = styled(Paper)(({ theme }) => ({
    backgroundColor: theme.palette.mode === "dark" ? "#1A2027" : "#fff",
    ...theme.typography.body2,
    padding: theme.spacing(2),
    width: 800,
    color: theme.palette.text.primary,
    borderBottomLeftRadius: "24px",
    borderBottomRightRadius: "0px",
    borderTopRightRadius: "24px",
    borderTopLeftRadius: "24px",
  }));

  const getStyledPaper = (message, index, direction = "start") => {
    if (direction === "start") {
      return (
        <Box alignSelf={"start"}>
          <HumanStyledPaper key={index}>
            <Grid container spacing={2} justifyContent={"center"}>
              <Grid item>
                <Avatar>B</Avatar>
              </Grid>
              <Grid item xs zeroMinWidth>
                <Typography noWrap>{message}</Typography>
              </Grid>
            </Grid>
          </HumanStyledPaper>
        </Box>
      );
    } else
      return (
        <Box alignSelf={"end"}>
          <BotStyledPaper key={index}>
            <Grid container spacing={2}>
              <Grid item xs zeroMinWidth>
                <Typography>{message}</Typography>
              </Grid>
              <Grid item>
                <Avatar>
                  <IconBook />
                </Avatar>
              </Grid>
            </Grid>
          </BotStyledPaper>
        </Box>
      );
  };

  return (
    // <IconButton
    //   variant="contained"
    //   onClick={() => handleLogin()}
    //   size="large"
    //   sx={{ height: "48px", width: "48px" }}
    //   disabled={lazy}
    //   color="secondary"
    // >
    //   <IconSend />
    // </IconButton>

    <Box width={"90vw"} height={"90vh"}>
      <Grid
        container
        spacing={2}
        alignContent={"space-between"}
        height={"100%"}
      >
        <Grid item xs={12}>
          <Stack spacing={2} sx={{ width: "100%" }}>
            {messages.map((message, index) => {
              return getStyledPaper(
                message.message,
                index,
                message.sender === "bot" ? "end" : "start"
              );
            })}
            <Box alignSelf={"end"} width={800}>
              {lazy ? (
                <Skeleton
                  variant="rounded"
                  height={120}
                  animation="pulse"
                  sx={{ bgcolor: "#fff", borderRadius: "24px" }}
                />
              ) : undefined}
            </Box>
          </Stack>
        </Grid>

        <Grid
          container
          item
          xs={12}
          spacing={2}
          justifyContent={"center"}
          alignItems={"center"}
          display={"flex"}
        >
          <Grid item xs={11}>
            <TextField
              id="fixed-input"
              label="Enter a prompt here"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              variant="filled"
              fullWidth
              sx={{
                backgroundColor: "white",
                borderRadius: "8px",
              }}
              multiline
              maxRows={1}
              onKeyDown={handleKeyDown}
            />
          </Grid>
          <Grid item>
            <IconButton
              variant="contained"
              onClick={() => handleClick(input)}
              size="large"
              sx={{ height: "48px", width: "48px" }}
              disabled={lazy}
              color="secondary"
            >
              <IconSend />
            </IconButton>
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
}

export default App;
