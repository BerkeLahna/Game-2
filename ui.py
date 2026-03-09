import pygame


def draw_ui_bar(screen,x,y,current,maximum,bar_image):

    ratio = max(0,min(1,current/maximum))
    img_w,img_h = bar_image.get_size()

    temp = pygame.Surface((img_w,img_h),pygame.SRCALPHA)
    temp.blit(bar_image,(0,0))

    start_pct,end_pct = 0.32,0.91
    top_pct,bottom_pct = 0.35,0.53

    fill_start = int(img_w*start_pct)
    total_width = int(img_w*end_pct)-fill_start

    fill_y = int(img_h*top_pct)
    fill_h = int(img_h*(bottom_pct-top_pct))

    empty = int(total_width*(1-ratio))

    if empty>0:
        rect = pygame.Rect(
            fill_start+(total_width-empty),
            fill_y,
            empty,
            fill_h
        )

        pygame.draw.rect(temp,(0,0,0,0),rect)

    screen.blit(temp,(x,y))